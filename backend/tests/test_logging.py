import logging

from app.core.config import settings
from app.core.logging import setup_logging

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def test_setup_logging_returns_root_logger():
    logger = setup_logging()
    assert isinstance(logger, logging.Logger)
    assert logger is logging.getLogger()


def test_root_logger_level_matches_settings():
    logger = setup_logging()
    assert logger.level == logging.getLevelName(settings.log_level)


def test_root_logger_has_one_handler():
    logger = setup_logging()
    assert len(logger.handlers) == 1


def test_handler_is_stream_handler():
    logger = setup_logging()
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)


def test_handler_has_consistent_format():
    logger = setup_logging()
    handler = logger.handlers[0]
    assert handler.formatter is not None
    assert handler.formatter._fmt == _LOG_FORMAT


def test_setup_logging_is_idempotent():
    setup_logging()
    setup_logging()
    root = logging.getLogger()
    assert len(root.handlers) == 1


def test_application_logger_inherits_from_root():
    setup_logging()
    app_logger = logging.getLogger("buildkit.test_module")
    assert app_logger.level == logging.NOTSET
    assert app_logger.handlers == []
    assert app_logger.propagate is True


def test_application_logger_emits_through_root():
    root = setup_logging()

    captured = []

    class _CaptureHandler(logging.Handler):
        def emit(self, record):
            captured.append(record)

    capture = _CaptureHandler(level=logging.DEBUG)
    root.addHandler(capture)
    try:
        app_logger = logging.getLogger("buildkit.emission_test")
        app_logger.info("test message")
        assert len(captured) == 1
        assert captured[0].message == "test message"
        assert captured[0].name == "buildkit.emission_test"
    finally:
        root.removeHandler(capture)


def test_log_level_override_via_settings(monkeypatch):
    monkeypatch.setattr(settings, "log_level", "DEBUG")
    logger = setup_logging()
    assert logger.level == logging.DEBUG


def test_log_level_warning_via_settings(monkeypatch):
    monkeypatch.setattr(settings, "log_level", "WARNING")
    logger = setup_logging()
    assert logger.level == logging.WARNING
