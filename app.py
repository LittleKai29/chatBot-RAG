import streamlit as st
from pymongo import MongoClient
import bcrypt

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["chatbot_db"]
users_col = db["users"]
chats_col = db["chats"]

def register_user(username, password):
    if users_col.find_one({"username": username}):
        return False  # Username đã tồn tại
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_col.insert_one({"username": username, "password": hashed_pw})
    return True

def login_user(username, password):
    user = users_col.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return True
    return False

# Giao diện chính
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    st.title("Đăng nhập vào Chatbot")
    username = st.text_input("Tên đăng nhập", key="login_username")
    password = st.text_input("Mật khẩu", type="password", key="login_password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Đăng nhập"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Đăng nhập thành công! Chuyển hướng...")
                st.experimental_rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")
    
    with col2:
        if st.button("Đăng ký"):
            st.session_state.page = "register"
            st.experimental_rerun()

elif st.session_state.page == "register":
    st.title("Đăng ký tài khoản")
    new_username = st.text_input("Tên đăng nhập", key="new_username")
    new_password = st.text_input("Mật khẩu", type="password", key="new_password")
    confirm_password = st.text_input("Nhập lại mật khẩu", type="password", key="confirm_password")
    
    if st.button("Xác nhận đăng ký"):
        if new_password == confirm_password:
            if register_user(new_username, new_password):
                st.success("Đăng ký thành công! Vui lòng đăng nhập.")
                st.session_state.page = "login"
                st.experimental_rerun()
            else:
                st.error("Tên đăng nhập đã tồn tại.")
        else:
            st.error("Mật khẩu không khớp.")
    
    if st.button("Quay lại đăng nhập"):
        st.session_state.page = "login"
        st.experimental_rerun()

# Chuyển sang màn hình chatbot nếu đăng nhập thành công
if "logged_in" in st.session_state and st.session_state.logged_in:
    chatbot_ui()
