import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
from bson import ObjectId

# Load environment variables
load_dotenv()

MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")

# Connect to MongoDB
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
client = MongoClient(mongo_uri)
db = client["chatbot_db"]
users_col = db["users"]
chats_col = db["chats"]

# User authentication functions
def register_user(username, password):
    if users_col.find_one({"username": username}):
        return False
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_col.insert_one({"username": username, "password": hashed_pw})
    return True

def login_user(username, password):
    user = users_col.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return True
    return False

# Chat functions
def get_chat_list(username):
    return list(chats_col.find({"username": username}, {"chat_id": 1, "title": 1}))

def get_chat_history(chat_id):
    chat = chats_col.find_one({"chat_id": chat_id})
    return chat["history"] if chat else []

def create_new_chat(username, title):
    chat_id = str(ObjectId())
    chats_col.insert_one({"username": username, "chat_id": chat_id, "title": title, "history": []})
    return chat_id

def save_chat(chat_id, message, response):
    chats_col.update_one({"chat_id": chat_id}, {"$push": {"history": {"message": message, "response": response}}})

# UI Handling
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    st.title("Đăng nhập vào Chatbot")
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Đăng nhập"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "chatbot"
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")
    with col2:
        if st.button("Đăng ký"):
            st.session_state.page = "register"
            st.rerun()

elif st.session_state.page == "register":
    st.title("Đăng ký tài khoản")
    new_username = st.text_input("Tên đăng nhập")
    new_password = st.text_input("Mật khẩu", type="password")
    confirm_password = st.text_input("Nhập lại mật khẩu", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Xác nhận đăng ký"):
            if new_password == confirm_password:
                if register_user(new_username, new_password):
                    st.success("Đăng ký thành công! Vui lòng đăng nhập.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("Tên đăng nhập đã tồn tại.")
            else:
                st.error("Mật khẩu không khớp.")
    with col2:
        if st.button("Quay lại đăng nhập"):
            st.session_state.page = "login"
            st.rerun()

# Chatbot UI
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
            st.markdown(f"**Bạn:** {msg['message']}")
            st.markdown(f"**Chatbot:** {msg['response']}")
            st.write("---")

        user_input = st.text_input("Nhập tin nhắn của bạn")
        if st.button("Gửi"):
            if user_input:
                bot_response = f"Bạn vừa nói: {user_input}"  # Placeholder chatbot response
                save_chat(chat_id, user_input, bot_response)
                st.rerun()

    # Tạo khoảng trống để đẩy nút đăng xuất xuống dưới cùng
    st.sidebar.markdown("<br>" * 20, unsafe_allow_html=True)

    # Nút đăng xuất
    if st.sidebar.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()

if "logged_in" in st.session_state and st.session_state.logged_in:
    st.session_state.page = "chatbot"
    chatbot_ui()
