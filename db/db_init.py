from pymongo import MongoClient
import time

client = MongoClient("mongodb://localhost:27017")
db = client["qr_wifi"]

# indexes
db.users.create_index("mobile", unique=True)
db.wallet.create_index("mobile", unique=True)
db.transactions.create_index("mobile")

# 🔥 SEED TEST USER (IMPORTANT FOR DEBUGGING)
db.users.update_one(
    {"mobile": "09933592644"},
    {
        "$setOnInsert": {
            "mobile": "09933592644",
            "status": "active",
            "created_at": time.time()
        }
    },
    upsert=True
)

db.wallet.update_one(
    {"mobile": "09933592644"},
    {
        "$setOnInsert": {
            "mobile": "09933592644",
            "seconds": 100,
            "devices_allowed": 3,
            "created_at": time.time()
        }
    },
    upsert=True
)

print("MongoDB initialized + test user created")
