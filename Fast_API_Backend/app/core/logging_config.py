import logging
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[2] / "app.log"


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == LOG_FILE
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s"
            )
        )
        logger.addHandler(handler)

    return logger
