from pymongo import MongoClient

uri = "mongodb+srv://santosh060878_db_user:gbOGkEMoz16mP9DN@cluster0.ayakfm7.mongodb.net/"

print("Attempting to connect...")
try:
    # 5 second timeout so we don't wait 30 seconds
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
