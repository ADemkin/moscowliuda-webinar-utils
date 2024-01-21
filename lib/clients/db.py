from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import connect
from typing import Generator

from lib.environment import env_str_field
from lib.paths import DB_PATH


@dataclass
class DB:
    path: str = env_str_field("DBPATH", "db.sqlite3")
    migrations: Path = field(default=DB_PATH / "migrations")
    timeout: int = 10

    @classmethod
    def create_in_memory(cls) -> "DB":
        return cls(path=":memory:")

    def _migrate(self) -> None:
        migration_paths = sorted(self.migrations.glob("*.sql"))
        migration_queries = [path.read_text() for path in migration_paths]
        with self.connection() as connection:
            for migration_query in migration_queries:
                connection.executescript(migration_query)

    def __post_init__(self) -> None:
        self._migrate()

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        connection = connect(self.path, timeout=self.timeout)
        try:
            yield connection
        except:  # noqa
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()
