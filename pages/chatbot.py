import streamlit as st
from connection import get_chat_list, get_chat_history, create_new_chat, save_chat

def send_message():
    if "chat_id" in st.session_state:
        chat_id = st.session_state["chat_id"]
        user_input = st.session_state["user_input"].strip()
        if user_input:
            bot_response = f"Bạn vừa nói: {user_input}"
            save_chat(chat_id, user_input, "user")
            save_chat(chat_id, bot_response, "ai")
            st.session_state["user_input"] = ""
            st.rerun()

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

        for msg in chats:
            if msg["role"] == "user":
                st.markdown(f"**Bạn:** {msg['message']}")
            elif msg["role"] == "ai":
                st.markdown(f"**Chatbot:** {msg['message']}")
            st.write("---")

        user_input = st.text_input("Nhập tin nhắn...", key="user_input", on_change=send_message)
        if st.button("Gửi"):
            send_message()

    st.sidebar.markdown("<br>" * 20, unsafe_allow_html=True)

    if st.sidebar.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()
