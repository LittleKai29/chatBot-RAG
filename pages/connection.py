import os
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

# Authentication functions
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

def save_chat(chat_id, message, role):
    """Lưu tin nhắn vào lịch sử hội thoại với role (user hoặc ai)."""
    chats_col.update_one(
        {"chat_id": chat_id},
        {"$push": {"history": {"role": role, "message": message}}},
        upsert=True
    )
