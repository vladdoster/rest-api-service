"""SQLAlchemy engine/session wiring plus the migration runner used at startup and in tests."""

from collections.abc import Iterator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"
# arbitrary but fixed: serialises `upgrade head` across tasks that start at the same time
MIGRATION_LOCK_ID = 7_355_608

settings = get_settings()

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    ),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped session."""
    with SessionLocal() as session:
        yield session


def run_migrations(target: Engine | None = None) -> None:
    """`alembic upgrade head` over one connection, under a transaction-scoped advisory lock.

    migrations/env.py reuses this connection, so alembic joins the open transaction and the
    lock is held until commit: concurrent tasks queue up, and the second finds nothing to apply.
    """
    config = Config(str(ALEMBIC_INI))
    with (target or engine).begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": MIGRATION_LOCK_ID})
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
