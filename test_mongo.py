import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
print(f"Connecting to: {uri.replace(uri.split('@')[0], 'mongodb+srv://<hidden>') if '@' in uri else uri}")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
