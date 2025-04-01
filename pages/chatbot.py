import time
import streamlit as st
from connection import get_chat_list, get_chat_history, create_new_chat, save_chat
from my_chatbot import BotLLM


bot_llm = BotLLM()


def send_message():
    if "chat_id" in st.session_state:
        chat_id = st.session_state["chat_id"]
        user_input = st.session_state.get("user_input", "").strip()

        if user_input:
            # 1. Hiển thị tin nhắn user trước
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Lưu tin nhắn user
            save_chat(chat_id, user_input, "user")

            # 2. Tạo một container riêng cho bot response
            chat_container = st.container()  # Thay st.empty() bằng container
            
            with chat_container:  # Đảm bảo vị trí response nằm đúng chỗ
                with st.chat_message("ai"):
                    message_placeholder = st.empty()
                    bot_response = ""
                    
                    # Stream response
                    for message_chunk, metadata in bot_llm.get_response(user_input, thread_id=chat_id):
                        if message_chunk.content:
                            bot_response += message_chunk.content
                            message_placeholder.markdown(bot_response + "▌")
                            time.sleep(0.08)
                    
                    # Hiển thị kết quả cuối cùng
                    message_placeholder.markdown(bot_response)
            
            # Lưu phản hồi AI
            save_chat(chat_id, bot_response, "ai")
            st.session_state["user_input"] = ""


def chatbot_ui():
    st.sidebar.title("Lịch sử trò chuyện")
    username = st.session_state.username
    chat_list = get_chat_list(username)
    chat_options = {chat["title"]: chat["chat_id"] for chat in chat_list}
    selected_chat_title = st.sidebar.selectbox("Chọn cuộc trò chuyện", ["Tạo cuộc trò chuyện mới"] + list(chat_options.keys()))

    if selected_chat_title == "Tạo cuộc trò chuyện mới":
        new_chat_title = st.sidebar.text_input("Tiêu đề cuộc trò chuyện")
        if st.sidebar.button("Tạo"):
            if new_chat_title:
                chat_id = create_new_chat(username, new_chat_title)
                st.session_state["chat_id"] = chat_id
                st.rerun()
    else:
        chat_id = chat_options[selected_chat_title]
        st.session_state["chat_id"] = chat_id

    if "chat_id" in st.session_state:
        chat_id = st.session_state["chat_id"]
        st.subheader(f"🗨️ {selected_chat_title}")
        chats = get_chat_history(chat_id)
        
        # Hiển thị toàn bộ lịch sử dùng st.chat_message
        for msg in chats:
            with st.chat_message(msg["role"]):  # "user" hoặc "ai"
                st.markdown(msg['message'])

        # Use `key="user_input"` to bind the widget to session state
        st.text_input("Nhập tin nhắn...", key="user_input", on_change=send_message)

    st.sidebar.markdown("<br>" * 20, unsafe_allow_html=True)

    if st.sidebar.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()
