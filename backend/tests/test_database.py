import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.database import Base, SessionLocal, engine, get_session


def test_database_url_default_is_postgresql():
    assert settings.database_url.startswith("postgresql+psycopg2://")


def test_engine_is_sqlalchemy_engine():
    assert isinstance(engine, Engine)


def test_engine_uses_postgresql_driver():
    assert engine.url.drivername == "postgresql+psycopg2"


def test_session_local_is_sessionmaker():
    assert isinstance(SessionLocal, sessionmaker)


def test_session_local_bound_to_engine():
    session = SessionLocal()
    try:
        assert session.bind is engine
    finally:
        session.close()


def test_base_has_metadata():
    assert hasattr(Base, "metadata")


def test_get_session_yields_session_bound_to_engine():
    gen = get_session()
    session = next(gen)
    assert isinstance(session, Session)
    assert session.bind is engine
    with pytest.raises(StopIteration):
        next(gen)
