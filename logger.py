import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

logger = logging.getLogger("quiz_app")

if not logger.handlers:
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        filename=LOG_FILE,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.propagate = False