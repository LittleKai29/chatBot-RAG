import streamlit as st
import pymongo
import bcrypt

# Kết nối MongoDB
def get_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    return client["chatbot_db"]

db = get_db()
users_col = db["users"]
chats_col = db["chats"]

# Hash mật khẩu
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Kiểm tra mật khẩu
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Đăng ký tài khoản
def register(username, password):
    if users_col.find_one({"username": username}):
        st.error("Tên đăng nhập đã tồn tại!")
        return

    users_col.insert_one({"username": username, "password_hash": hash_password(password)})
    st.success("Đăng ký thành công!")

# Đăng nhập
def login(username, password):
    user = users_col.find_one({"username": username})
    if user and check_password(password, user["password_hash"]):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.experimental_rerun()
    else:
        st.error("Sai tên đăng nhập hoặc mật khẩu!")

# Lấy lịch sử chat
def get_chat_history(username):
    chat = chats_col.find_one({"username": username})
    return chat["history"] if chat else []

# Lưu chat
def save_chat(username, message, response):
    chat = chats_col.find_one({"username": username})
    if chat:
        chats_col.update_one({"username": username}, {"$push": {"history": {"message": message, "response": response}}})
    else:
        chats_col.insert_one({"username": username, "history": [{"message": message, "response": response}]})

# Giao diện chatbot
def chatbot_ui():
    st.title("Chatbot")

    # Hiển thị lịch sử chat
    st.subheader("Lịch sử chat")
    chats = get_chat_history(st.session_state["username"])
    for msg in chats:
        st.text_area("Bạn:", value=msg["message"], height=50, disabled=True)
        st.text_area("Chatbot:", value=msg["response"], height=50, disabled=True)

    # Ô nhập tin nhắn
    st.subheader("Nhập tin nhắn")
    user_input = st.text_input("Nhập tin nhắn của bạn")

    if st.button("Gửi"):
        if user_input:
            bot_response = f"Bạn vừa nói: {user_input}"  # TODO: Thay bằng AI thật
            save_chat(st.session_state["username"], user_input, bot_response)
            st.experimental_rerun()

    # Đăng xuất
    if st.sidebar.button("Đăng xuất"):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.experimental_rerun()

# Giao diện đăng nhập / đăng ký
def login_ui():
    st.title("Đăng nhập / Đăng ký")

    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")

        col1, col2 = st.columns(2)
        with col1:
            register_button = st.form_submit_button("Đăng ký")
        with col2:
            login_button = st.form_submit_button("Đăng nhập")

    if register_button:
        if username and password:
            register(username, password)
        else:
            st.warning("Vui lòng nhập đủ thông tin!")

    if login_button:
        if username and password:
            login(username, password)
        else:
            st.warning("Vui lòng nhập đủ thông tin!")

# Điều hướng giữa đăng nhập và chatbot
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login_ui()
else:
    chatbot_ui()