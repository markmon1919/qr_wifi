import time
from api.models import db, get_devices, get_wallet, set_wallet, remove_device

INTERVAL = 5


def run_engine():
    while True:
        time.sleep(INTERVAL)

        users = list(db.wallet.find())

        for user in users:

            mobile = user["mobile"]
            devices = get_devices(mobile)

            if not devices:
                continue

            wallet = get_wallet(mobile)

            drain = len(devices)
            new_balance = max(0, wallet - drain)

            set_wallet(mobile, new_balance)

            if new_balance <= 0:
                for mac in devices:
                    remove_device(mobile, mac)
                    