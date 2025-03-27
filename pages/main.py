import streamlit as st
from pages.auth_pages import login_page, register_page
from pages.chatbot import chatbot_ui

if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.logged_in:
    chatbot_ui()
