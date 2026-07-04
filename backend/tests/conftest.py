import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.data import books, borrowings, members
from backend.app.database import Base, get_db
from backend.app.models.book import Book
from backend.app.models.borrowing import Borrowing
from backend.app.models.member import Member


ROOT_DIR = Path(__file__).resolve().parents[2]
test_env = {
    **dotenv_values(ROOT_DIR / ".env.test"),
    **os.environ,
}

test_db_name = test_env.get("DB_NAME", "")
if not test_db_name.endswith("_test"):
    raise RuntimeError(
        "Tests require .env.test with a DB_NAME ending in '_test'; "
        "refusing to use a development database."
    )

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=test_env.get("DB_USER"),
    password=test_env.get("DB_PASSWORD"),
    host=test_env.get("DB_HOST", "localhost"),
    port=int(test_env.get("DB_PORT", 5432)),
    database=test_db_name,
)
engine = create_engine(TEST_DATABASE_URL)


def override_get_db():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    """Reset the dedicated PostgreSQL test database before every test."""
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.execute(
            text(
                "TRUNCATE TABLE borrowings, members, books "
                "RESTART IDENTITY CASCADE"
            )
        )
        session.add_all(Book(**book) for book in books)
        session.add_all(Member(**member) for member in members)
        session.flush()
        session.add_all(Borrowing(**borrowing) for borrowing in borrowings)
        session.flush()
        for table, id_column in (
            ("books", "book_id"),
            ("members", "member_id"),
            ("borrowings", "borrowing_id"),
        ):
            session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{id_column}'), "
                    f"MAX({id_column}), true) FROM {table}"
                )
            )
        session.commit()

    yield
