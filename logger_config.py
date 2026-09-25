import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "banking_support.log"


def setup_logger():
    logger = logging.getLogger("BankingSupportAI")

    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


logger = setup_logger()