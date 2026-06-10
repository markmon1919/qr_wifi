from pymongo import MongoClient
import redis, time

# -------------------------
# DB CONNECTION
# -------------------------
mongo = MongoClient("mongodb://localhost:27017")
db = mongo["qr_wifi"]

r = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True
)

DEFAULT_DEVICE_LIMIT = 3

# TTL SETTINGS
DEVICE_TTL = 60 * 60 * 24   # 24 hours
MAC_TTL = 60 * 60 * 24      # 24 hours


# -------------------------
# 🔥 TTL REFRESH (NEW)
# -------------------------
def refresh_session(mobile: str, mac: str):
    """
    Refresh Redis TTL for active session
    """
    r.expire(f"devices:{mobile}", DEVICE_TTL)
    r.expire(f"mac:{mac}", MAC_TTL)


# -------------------------
# USER / WALLET
# -------------------------
def get_or_create_user(mobile: str):
    user = db.users.find_one({"mobile": mobile})

    if not user:
        db.users.insert_one({
            "mobile": mobile,
            "status": "active",
            "created_at": time.time()
        })

    wallet = db.wallet.find_one({"mobile": mobile})

    if not wallet:
        db.wallet.insert_one({
            "mobile": mobile,
            "seconds": 0,
            "devices_allowed": DEFAULT_DEVICE_LIMIT,
            "created_at": time.time()
        })

    print("CREATING USER:", mobile)

    return db.wallet.find_one({"mobile": mobile})


def get_wallet_document(mobile: str):
    wallet = db.wallet.find_one({"mobile": mobile})

    if not wallet:
        get_or_create_user(mobile)
        wallet = db.wallet.find_one({"mobile": mobile})

    return wallet


def get_wallet(mobile: str):
    return get_wallet_document(mobile)["seconds"]


def set_wallet(mobile: str, seconds: int):
    db.wallet.update_one(
        {"mobile": mobile},
        {"$set": {"seconds": seconds}},
        upsert=True
    )


# -------------------------
# DEVICE MANAGEMENT
# -------------------------
def add_device(mobile: str, mac: str):
    key = f"devices:{mobile}"

    r.sadd(key, mac)
    r.expire(key, DEVICE_TTL)   # initial TTL


def remove_device(mobile: str, mac: str):
    r.srem(f"devices:{mobile}", mac)


def get_devices(mobile: str):
    return list(r.smembers(f"devices:{mobile}"))


# -------------------------
# MAC BINDING
# -------------------------
def bind_mac(mac: str, mobile: str):
    key = f"mac:{mac}"

    r.set(key, mobile)
    r.expire(key, MAC_TTL)   # initial TTL


def resolve_mac(mac: str):
    return r.get(f"mac:{mac}")


# -------------------------
# TOPUP
# -------------------------
def topup_wallet(mobile: str, seconds: int, reference: str = "manual"):
    get_or_create_user(mobile)

    db.wallet.update_one(
        {"mobile": mobile},
        {"$inc": {"seconds": seconds}},
        upsert=True
    )

    db.transactions.insert_one({
        "mobile": mobile,
        "type": "topup",
        "seconds": seconds,
        "reference": reference,
        "timestamp": time.time()
    })
    