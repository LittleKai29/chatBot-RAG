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

    menu = ["Đăng nhập", "Đăng ký"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Đăng nhập":
        st.subheader("Đăng nhập")
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if login(username, password):
                st.write(f"Chào mừng {username}!")

    elif choice == "Đăng ký":
        st.subheader("Đăng ký")
        new_username = st.text_input("Tên đăng nhập mới")
        new_password = st.text_input("Mật khẩu mới", type="password")
        confirm_password = st.text_input("Nhập lại mật khẩu", type="password")

        if st.button("Đăng ký"):
            if register(new_username, new_password, confirm_password):
                st.write(f"Chào mừng {new_username}!")

if __name__ == "__main__":
    main()
