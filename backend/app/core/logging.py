import logging
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging() -> logging.Logger:
    """Configure the root logger with a console handler at the configured log level.

    Application modules obtain loggers via ``logging.getLogger(__name__)``;
    after this function is called, those loggers automatically use the
    configured level and format through propagation to the root logger.

    Calling this function replaces any existing handlers on the root logger,
    so it is safe to call more than once (e.g. during testing or reloads).
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove existing handlers to ensure a clean, consistent configuration.
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(console_handler)

    return root_logger
