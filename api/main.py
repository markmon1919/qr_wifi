from fastapi import FastAPI
from api.models import *

app = FastAPI()

DEFAULT_DEVICE_LIMIT = 3


@app.get("/")
def root():
    return {
        "status": "ISP V6 API RUNNING",
        "endpoints": ["/v6/login", "/v6/check", "/v6/topup", "/v6/user/{mobile}"]
    }


# -------------------------
# LOGIN
# -------------------------
@app.post("/v6/login")
def login(data: dict):

    mobile = data["mobile"].strip()
    mac = data["mac"].lower()

    get_or_create_user(mobile)

    wallet = get_wallet_document(mobile)

    if wallet["seconds"] <= 0:
        return {
            "allowed": False,
            "reason": "No wallet balance",
            "mobile": mobile
        }

    devices = get_devices(mobile)
    limit = wallet.get("devices_allowed", DEFAULT_DEVICE_LIMIT)

    if mac not in devices and len(devices) >= limit:
        return {
            "allowed": False,
            "reason": "Device limit reached"
        }

    add_device(mobile, mac)
    bind_mac(mac, mobile)

    # 🔥 TTL REFRESH
    refresh_session(mobile, mac)

    print("LOGIN HIT:", mobile)

    # 🔥 refresh device count AFTER update
    updated_devices = get_devices(mobile)

    return {
        "allowed": True,
        "mobile": mobile,
        "wallet_seconds": wallet["seconds"],
        "active_devices": len(updated_devices),
        "device_limit": limit
    }


# -------------------------
# CHECK
# -------------------------
@app.get("/v6/check")
def check(mac: str):

    mobile = resolve_mac(mac.lower())

    if not mobile:
        return {"allowed": False}

    seconds = get_wallet(mobile)

    return {
        "allowed": seconds > 0,
        "mobile": mobile,
        "wallet_seconds": seconds
    }


# -------------------------
# TOPUP
# -------------------------
@app.post("/v6/topup")
def topup(data: dict):

    mobile = data["mobile"]
    seconds = int(data["seconds"])
    reference = data.get("reference", "manual")

    topup_wallet(mobile, seconds, reference)

    return {
        "ok": True,
        "mobile": mobile,
        "added": seconds
    }


# -------------------------
# USER INFO
# -------------------------
@app.get("/v6/user/{mobile}")
def user(mobile: str):

    user = db.users.find_one({"mobile": mobile}, {"_id": 0})
    wallet = db.wallet.find_one({"mobile": mobile}, {"_id": 0})

    if not user:
        return {"exists": False}

    return {
        "exists": True,
        "user": user,
        "wallet": wallet,
        "devices": get_devices(mobile)
    }
