import streamlit as st
from connection import register_user, login_user

def login_page():
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

def register_page():
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