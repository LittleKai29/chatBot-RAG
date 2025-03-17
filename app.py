import streamlit as st
from pymongo import MongoClient

# Kết nối với MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["user_database"]
users_collection = db["users"]

# Hàm đăng nhập
def login(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        st.success("Đăng nhập thành công!")
        return True
    else:
        st.error("Tên đăng nhập hoặc mật khẩu không đúng.")
        return False

# Hàm đăng ký
def register(username, password, confirm_password):
    if password != confirm_password:
        st.error("Mật khẩu nhập lại không khớp.")
        return False
    if users_collection.find_one({"username": username}):
        st.error("Tên đăng nhập đã tồn tại.")
        return False
    users_collection.insert_one({"username": username, "password": password})
    st.success("Đăng ký thành công!")
    return True

# Giao diện chính
def main():
    st.title("Đăng nhập và Đăng ký")

    # Kiểm tra trạng thái hiện tại (đăng nhập hoặc đăng ký)
    if "show_register" not in st.session_state:
        st.session_state["show_register"] = False

    # Hiển thị màn hình đăng nhập hoặc đăng ký
    if not st.session_state["show_register"]:
        # Màn hình đăng nhập
        st.subheader("Đăng nhập")
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")

        col1, col2 = st.columns(2)  # Tạo 2 cột để đặt nút đăng nhập và đăng ký
        with col1:
            if st.button("Đăng nhập"):
                if login(username, password):
                    st.write(f"Chào mừng {username}!")
        with col2:
            if st.button("Đăng ký"):
                st.session_state["show_register"] = True  # Chuyển sang màn hình đăng ký

    else:
        # Màn hình đăng ký
        st.subheader("Đăng ký")
        new_username = st.text_input("Tên đăng nhập mới")
        new_password = st.text_input("Mật khẩu mới", type="password")
        confirm_password = st.text_input("Nhập lại mật khẩu", type="password")

        if st.button("Đăng ký tài khoản"):
            if register(new_username, new_password, confirm_password):
                st.session_state["show_register"] = False  # Quay lại màn hình đăng nhập sau khi đăng ký thành công

if __name__ == "__main__":
    main()
