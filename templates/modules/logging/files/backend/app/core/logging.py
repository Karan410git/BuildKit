import logging
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging() -> logging.Logger:
    """Configure reusable console logging from centralized settings."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(console_handler)
    return root_logger
