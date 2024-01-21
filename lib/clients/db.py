import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from pathlib import Path
from typing import Generator

from lib.environment import env_str_field
from lib.paths import DB_PATH


@dataclass
class DB:
    path: str = env_str_field("DBPATH", "db.sqlite3")
    migrations: Path = field(default=DB_PATH / "migrations")

    @classmethod
    def create_in_memory(cls) -> "DB":
        return cls(path=":memory:")

    def _migrate(self) -> None:
        migration_paths = sorted(self.migrations.glob("*.sql"))
        migration_queries = [path.read_text() for path in migration_paths]
        with self.safe_cursor() as cursor:
            for migration_query in migration_queries:
                cursor.executescript(migration_query)

    def __post_init__(self) -> None:
        self._migrate()

    @cached_property
    def connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    @property
    def cursor(self) -> sqlite3.Cursor:
        return self.connection.cursor()

    @contextmanager
    def safe_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        cursor = self.cursor
        try:
            yield cursor
        finally:
            cursor.close()
