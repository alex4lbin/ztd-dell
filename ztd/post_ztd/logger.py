import logging
from logging.handlers import RotatingFileHandler


def create_logger(name: str) -> logging.Logger:
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    file_handler = RotatingFileHandler(
        "/vagrant/ztd.log", maxBytes=4096 * 20, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    root.addHandler(file_handler)
    logger = logging.getLogger(name)
    return logger


logger = create_logger("post_ztd")
