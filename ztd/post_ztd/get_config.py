import csv

from devices import DellOS10
from logger import logger
from netmiko import (
    ConnectHandler,
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

CONFIG = "/vagrant/device_info.csv"
COMMANDS = "/vagrant/commands.txt"


def create_device(ip: str, passwd: str = None) -> DellOS10:
    if passwd is None:
        passwd = get_password_by_ip(ip)
    return DellOS10(host=ip, password=passwd)


def get_password_by_ip(ip: str) -> str:
    with open(CONFIG) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("ip") == ip:
                return row.get("passwd")


def get_commands(path: str) -> list[str]:
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]


def run_commands(handler: ConnectHandler, commands: list[str]) -> str:
    ip = handler.host
    output = handler.find_prompt() + " "
    for command in commands:
        logger.info(f"[{ip}] Sending '{command}'")
        output += handler.send_command(command, strip_command=False, strip_prompt=False)
    return output


def get_config(sw: DellOS10) -> None:
    ip = sw.host
    logger.info(f"Connecting to {ip}")
    try:
        handler = ConnectHandler(**sw.as_dict())
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        logger.critical(f"Could not SSH to {ip}: {e}")
        return
    logger.info(f"[{ip}] Getting running configuration")
    hostname = handler.find_prompt().strip("#")
    output = handler.send_command("show running-configuration")
    with open(f"{hostname}_run.log", "w") as f:
        f.write(output)
    # get result of show commands
    commands = get_commands(COMMANDS)
    logger.info(f"[{ip}] Running show commands")
    output = run_commands(handler, commands)
    with open(f"{hostname}_show.log", "w") as f:
        f.write(output)
    handler.disconnect()
    logger.info(f"[{ip}] Success!")


def main() -> None:
    with open(CONFIG) as f:
        reader = csv.DictReader(f)
        switches = [
            DellOS10(host=row.get("ip"), password=row.get("passwd")) for row in reader
        ]
    for sw in switches:
        get_config(sw)


if __name__ == "__main__":
    main()
