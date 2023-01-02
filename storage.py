from typing import Any
from tempfile import NamedTemporaryFile
from pathlib import Path
import atexit
import json


class StorageError(Exception):
    pass


DEFAULT_STORE = {
    "morph": {
        "name": {},
    },
    "webinars": {},
}
DEFAULT_FILE_NAME = "storage.json"


class Storage:
    def __init__(self, store: dict[str, Any], file: Path) -> None:
        self._store = store
        self._file = file

    @classmethod
    def temporary(cls) -> "Storage":
        file = NamedTemporaryFile()
        atexit.register(file.close)
        return cls(
            store=DEFAULT_STORE,
            file=Path(file.name),
        )

    @classmethod
    def create(cls) -> "Storage":
        file = Path(DEFAULT_FILE_NAME)
        if not file.exists():
            file.write_bytes(cls.dumps(DEFAULT_STORE))
        store = cls.loads(file.read_bytes())
        return Storage(store, DEFAULT_FILE_NAME)

    @staticmethod
    def dumps(data: dict[str, Any]) -> bytes:
        return json.dumps(
            data,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
        ).encode("utf-8")

    @staticmethod
    def loads(data_raw: bytes) -> dict[str, Any]:
        return json.loads(data_raw)

    def store(self) -> None:
        """Store current storage in file"""
        self._file.write_bytes(self.dumps(self._store))

    def set_name_morph(self, name: str, name_datv: str) -> None:
        if exists := self._store["morph"]["name"].get(name):
            raise StorageError(f"Name {name!r} already known as {exists!r}")
        self._store["morph"]["name"][name] = name_datv
        self.store()

    def get_name_morph(self, name: str) -> str | None:
        return self._store["morph"]["name"].get(name)

    def add_webinar(self, webinar_info: dict) -> int:
        for webinar_id, webinar in self._store["webinars"].items():
            if webinar_info == webinar:
                return webinar_id
        webinar_id = len(self._store["webinars"])
        self._store["webinars"][webinar_id] = webinar_info
        self.store()
        return webinar_id
