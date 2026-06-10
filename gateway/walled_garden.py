from flask import Flask, redirect, request

app = Flask(__name__)

VPS_IP = "172.16.0.132"
PORTAL = f"http://{VPS_IP}:7777"

BLOCKED = set()


@app.before_request
def guard():
    mac = request.headers.get("X-MAC", "TEST")

    if mac in BLOCKED:
        return redirect(PORTAL)


@app.route("/")
def internet():
    return "BLOCKED INTERNET"


@app.route("/block/<mac>")
def block(mac):
    BLOCKED.add(mac)
    return f"blocked {mac}"


@app.route("/unblock/<mac>")
def unblock(mac):
    BLOCKED.discard(mac)
    return f"unblocked {mac}"


if __name__ == "__main__":
    app.run(port=8080)
