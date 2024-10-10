from dataclasses import dataclass, asdict

@dataclass
class DellOS10:
    host: str
    device_type: str = "dell_os10"
    username: str = "admin"
    password: str = "admin"

    def as_dict(self):
        return asdict(self)
