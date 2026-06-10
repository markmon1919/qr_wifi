from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

VPS_IP = "172.16.0.132"


@app.route("/")
def portal():
    mac = request.args.get("mac", "unknown")

    return render_template_string("""
    <html>
    <head>
        <title>WiFi Login</title>
    </head>

    <body>
        <h2>Welcome to WiFi</h2>

        <form method="POST" action="/login">
            <input name="mobile" placeholder="Mobile Number" required>
            <input name="mac" value="{{mac}}" hidden>
            <button type="submit">Connect</button>
        </form>
    </body>
    </html>
    """, mac=mac)


@app.route("/login", methods=["POST"])
def login():
    r = requests.post(
        f"http://{VPS_IP}:8000/v6/login",
        json={
            "mobile": request.form["mobile"],
            "mac": request.form["mac"]
        }
    )

    result = r.json()

    if result.get("allowed"):
        return """
        <h3>Connected ✅</h3>
        <script>
            setTimeout(() => {
                window.location = "http://google.com"
            }, 2000);
        </script>
        """
    else:
        return "<h3>Blocked ❌</h3>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)
