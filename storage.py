import json
from pathlib import Path
from typing import Any, Sequence


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
    def from_path(cls, file_path: Path) -> "Storage":
        content = file_path.read_bytes()
        if not content:
            file_path.write_bytes(cls.dumps(DEFAULT_STORE))
            content = file_path.read_bytes()
        return Storage(cls.loads(content), file_path)

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

    def add_webinar(self, webinar_info: dict[str, str | int]) -> int:
        for webinar_id, webinar in self._store["webinars"].items():
            if webinar_info == webinar:
                return webinar_id
        webinar_id = len(self._store["webinars"])
        self._store["webinars"][webinar_id] = webinar_info
        self.store()
        return webinar_id

    def get_webinar(self, webinar_id: int) -> dict[str, str | int] | None:
        return self._store["webinars"].get(webinar_id)

    def list_webinars(self) -> Sequence[dict[str, str | int]]:
        return list(self._store["webinars"].values())
