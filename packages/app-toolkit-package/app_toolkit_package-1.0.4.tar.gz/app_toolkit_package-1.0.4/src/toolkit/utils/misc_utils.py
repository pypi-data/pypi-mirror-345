import hashlib
import logging
import os
import sys
from datetime import datetime

from ..repo.db.exceptions import AlreadyExists
from ..types_app import _F

logging.basicConfig(level=logging.INFO)


def logger(prefix: str = "==="):
    def decor(f: _F):
        async def wrapper(*args, **kwargs):
            logging.info(f"{prefix} Loading {f.__name__} data")
            try:
                created = await f(*args, **kwargs)
            except AlreadyExists:
                logging.info(f"{f.__name__} data already exists... exiting.")
                return None
            logging.info(f"{prefix} {created}")
            return created

        return wrapper

    return decor


def sha256_hash(input_string: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(input_string.encode("utf-8"))
    return sha256.hexdigest()


def get_time_now() -> datetime:
    """Equal to dt.now() at the moment."""
    # TODO: add timezone
    return datetime.now()


def set_sys_path_cwd() -> None:
    """sys.path.append(os.getcwd())."""
    sys.path.append(os.getcwd())
