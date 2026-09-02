"""Alembic environment. The URL comes from app settings (DB_* env vars) unless the caller
hands over an open connection through config.attributes, as app.db.run_migrations does."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

from app.db import engine
from app.models import Base

config = context.config
if config.config_file_name is not None:
    # keep the app's loggers alive when this runs inside the service process
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=engine.url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_with(connection: Connection) -> None:
    # begin_transaction() is a no-op when the connection is already in one (startup path)
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    shared = config.attributes.get("connection")
    if shared is not None:
        run_migrations_with(shared)
        return
    with engine.connect() as connection:
        run_migrations_with(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
