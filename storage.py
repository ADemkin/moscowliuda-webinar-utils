from typing import Any
from tempfile import NamedTemporaryFile
from pathlib import Path
import atexit
import json


class StorageError(Exception):
    pass


class Storage:
    def __init__(self, store: dict[str, Any], file: Path) -> None:
        self._store = store
        self._file = file

    @classmethod
    def temporary(cls) -> 'Storage':
        file = NamedTemporaryFile()
        atexit.register(file.close)
        return cls(
            store={
                'morph': {
                    'name': {},
                },
            },
            file=Path(file.name),
        )

    def dumps(self) -> None:
        """Store current storage in file"""
        raw_data = json.dumps(
            self._store,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
        )
        self._file.write_bytes(raw_data.encode('utf-8'))

    def set_name_morph(self, name: str, name_datv: str) -> None:
        if exists := self._store['morph']['name'].get(name):
            raise StorageError(f'Name {name!r} already known as {exists!r}')
        self._store['morph']['name'][name] = name_datv
        self.dumps()

    def get_name_morph(self, name: str) -> str | None:
        return self._store['morph']['name'].get(name)
