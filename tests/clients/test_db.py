from pathlib import Path

import pytest

from lib.clients.db import DB


@pytest.fixture
def db(tmp_path: Path) -> DB:
    query = """
        DROP TABLE IF EXISTS test;
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            name TEXT
        );
    """
    return DB(
        path=tmp_path / "test.sqlite3",
        migrations=[query],
    )


def test_db_migrations_applied_on_init(tmp_path: Path) -> None:
    migrations = [
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)",
        "CREATE TABLE IF NOT EXISTS test2 (id INTEGER PRIMARY KEY, name TEXT)",
    ]
    db = DB(
        path=tmp_path / "test.sqlite3",
        migrations=migrations,
    )
    with db.connection() as connection:
        connection.execute("INSERT INTO test (name) VALUES ('a')")
        connection.execute("INSERT INTO test2 (name) VALUES ('a')")


def test_db_commit_successful_transaction(db: DB) -> None:
    with db.connection() as connection:
        query = "INSERT INTO test (name) VALUES (:name)"
        params = {"name": "test"}
        connection.execute(query, params)
    with db.connection() as connection:
        row = connection.execute("SELECT COUNT(*) FROM test").fetchone()
    assert row[0] == 1


def test_db_drop_failed_transaction(db: DB) -> None:
    def _raise_inside_transaction() -> None:
        with db.connection() as connection:
            query = "INSERT INTO test (name) VALUES (:name)"
            params = {"name": "test"}
            raise Exception("Test exception")
            connection.execute(query, params)  # type: ignore

    with pytest.raises(Exception, match="Test exception"):
        _raise_inside_transaction()

    with db.connection() as connection:
        row = connection.execute("SELECT COUNT(*) FROM test").fetchone()
    assert row[0] == 0
