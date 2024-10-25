from threading import Thread

from flask import Flask, request
from get_config import create_device, get_config
from logger import logger

app = Flask(__name__)


@app.route("/kickstart", methods=["POST"])
def kickstart():
    if request.is_json:
        data = request.json
        if data.get("data") == "GO!!":
            ip = request.headers.get("X-Real-Ip")
            logger.info(f"Recieved POST from {ip}. Deployment finished.")
            sw = create_device(ip)
            t = Thread(target=get_config, args=(sw,))
            t.start()
            return "OK", 200
    return "FAIL", 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
