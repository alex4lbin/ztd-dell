import copy
import csv
import json
import os

from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

CONFIG = "/vagrant/device_info.csv"
TEMPLATES = "templates"
IP_BASE = os.getenv("IP_BASE")
URL_BASE = f"http://{IP_BASE}/ztd"


def read_config(path: str) -> list[dict]:
    with open(path) as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def create_dhcp_config(data: list[dict]) -> None:
    reservation = {
        "hw-address": "",
        "ip-address": "",
        "option-data": [{"name": "ztd-provision-url", "data": ""}],
    }
    reservations = []
    for entry in data:
        reservation_cp = copy.deepcopy(reservation)
        reservation_cp["hw-address"] = entry.get("mac")
        reservation_cp["ip-address"] = entry.get("ip")
        reservation_cp["option-data"][0]["data"] = f"{URL_BASE}/{entry.get('host')}.sh"
        reservations.append(reservation_cp)
    with open(f"{TEMPLATES}/dhcp.json") as f:
        config = json.load(f)
        config["Dhcp4"]["subnet4"][0]["reservations"] = reservations
    with open("kea-dhcp4.conf", "w") as f:
        json.dump(config, f, indent=2)


def create_provisioning_scripts(data: list[dict]) -> None:
    with open(f"{TEMPLATES}/ztd_script.j2") as f:
        template = Template(f.read())
    for entry in data:
        host = entry.get("host")
        output = template.render(ip_base=IP_BASE, host=host)
        with open(f"{host}.sh", "w") as f:
            f.write(output)
    with open(f"{TEMPLATES}/post_ztd.j2") as f:
        template = Template(f.read())
    output = template.render(ip_base=IP_BASE)
    with open("post_ztd.sh", "w") as f:
        f.write(output)


def main() -> None:
    data = read_config(CONFIG)
    create_dhcp_config(data)
    create_provisioning_scripts(data)


if __name__ == "__main__":
    main()
