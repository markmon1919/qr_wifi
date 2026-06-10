import requests

VPS_IP = "172.16.0.132"
API = f"http://{VPS_IP}:8000/v6/check"


def enforce(mac):
    r = requests.get(API, params={"mac": mac})
    data = r.json()

    if data.get("allowed"):
        print("ALLOW", mac)
    else:
        print("BLOCK", mac)
        