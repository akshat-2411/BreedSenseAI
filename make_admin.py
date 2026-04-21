import sys
from pymongo import MongoClient
from config import Config

def make_admin(email: str):
    print(f"Connecting to MongoDB at {Config.MONGO_URI}...")
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB_NAME]
    
    result = db.users.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )
    
    if result.matched_count > 0:
        if result.modified_count > 0:
            print(f"✅ Successfully upgraded '{email}' to the 'admin' role.")
        else:
            print(f"ℹ️ User '{email}' is already an admin.")
    else:
        print(f"❌ User with email '{email}' not found in the database. Did you register first?")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <user_email>")
        sys.exit(1)
        
    email_to_upgrade = sys.argv[1]
    make_admin(email_to_upgrade)
