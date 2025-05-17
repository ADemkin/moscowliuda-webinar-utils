from collections.abc import Generator
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import connect

from lib.environment import env_str_field
from lib.paths import DB_PATH


def discover_migrations(migrations_dir: Path) -> Sequence[str]:
    migration_paths = sorted(migrations_dir.glob("*.sql"))
    return [path.read_text() for path in migration_paths]


@dataclass(frozen=True, slots=True)
class DB:
    path: str | Path = env_str_field("DBPATH", "db.sqlite3")  # or ":memory:"
    migrations: Sequence[str] = field(
        default_factory=partial(discover_migrations, DB_PATH / "migrations"),
    )
    timeout: int = 5

    def __post_init__(self) -> None:
        with self.connection() as connection:
            for migration in self.migrations:
                connection.executescript(migration)

    def get_connection(self) -> Connection:
        return connect(self.path, timeout=self.timeout)

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        connection = self.get_connection()
        try:
            yield connection
        except:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()
