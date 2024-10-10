import logging
import csv
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException

from devices import DellOS10

CONFIG = "/vagrant/device_info.csv"

app = Flask(__name__)

file_handler = RotatingFileHandler('/vagrant/ztd.log',
                                    maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

@app.route("/kickstart", methods=['POST'])
def kickstart():
    if request.is_json:
        data = request.json
        if data.get("data") == "GO!!":
            ip = request.headers.get("X-Real-Ip")
            app.logger.info(f"Recieved POST from {ip}. Deployment finished.")
            get_config(ip)
            return "OK",200
    return "FAIL",400

def run_commands(handler: ConnectHandler, commands: list[str]) -> str:
    ip = handler.host
    output = handler.find_prompt() + " "
    for command in commands:
        app.logger.info(f"[{ip}] Sending '{command}'")
        output += handler.send_command(command, strip_command=False, strip_prompt=False)
    return output

def get_commands(path: str) -> list[str]:
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]
    
def get_password(ip: str) -> str:
    with open(CONFIG) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("ip") == ip:
                return row.get("passwd")

def get_config(ip) -> None:
    password = get_password(ip)
    sw = DellOS10(host=ip, password=password)
    app.logger.info(f"Connecting to {ip}")
    try:
        handler = ConnectHandler(**sw.as_dict())
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        app.logger.critical(f"Could not SSH to {ip}: {e}")
        return
    app.logger.info(f"[{ip}] Getting running configuration")
    hostname = handler.find_prompt().strip("#")
    output = handler.send_command("show running-configuration")
    with open(f"{hostname}_run.log", "w") as f:
        f.write(output)
    # get result of show commands
    commands = get_commands("commands.txt")
    app.logger.info(f"[{ip}] Running show commands")
    output = run_commands(handler, commands)
    with open(f"{hostname}_show.log", "w") as f:
        f.write(output)
    handler.disconnect()
    app.logger.info(f"[{ip}] Success!")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")