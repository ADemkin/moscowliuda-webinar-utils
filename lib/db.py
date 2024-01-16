import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from pathlib import Path
from typing import Generator

from lib.environment import env_str_field


@dataclass(slots=True)
class DB:
    path: str = env_str_field("DBPATH", "db.sqlite3")
    migrations: Path = field(default_factory=partial(Path, "migrations"))
    _connection: sqlite3.Connection | None = field(
        init=False, repr=False, default=None
    )

    def _migrate(self) -> None:
        migrations = [
            migration_path.read_text()
            for migration_path in sorted(self.migrations.glob("*.sql"))
        ]
        with self.safe_cursor() as cursor:
            for migration in migrations:
                cursor.executescript(migration)

    def __post_init__(self) -> None:
        self._migrate()

    @classmethod
    def create_in_memory(cls) -> "DB":
        return cls(path=":memory:")

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.path)
        return self._connection

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
