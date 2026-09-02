"""Real-Postgres fixtures: one container per session, one rolled-back transaction per test.

The app's own engine (app.db.engine, built at import from DB_* settings) is never used here:
tests build their own engine from the container URL, run the migrations through it, and swap
the get_db dependency. Importing app.db is harmless because engines connect lazily.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

from app.db import get_db, run_migrations
from app.main import app

# same image as docker-compose.yml; public ECR avoids Docker Hub pull limits
POSTGRES_IMAGE = "public.ecr.aws/docker/library/postgres:17-alpine"


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        engine = create_engine(postgres.get_connection_url())
        run_migrations(engine)
        yield engine
        engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    # the router's session.commit() only releases a savepoint; the outer transaction rolls back
    with db_engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        transaction.rollback()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)
