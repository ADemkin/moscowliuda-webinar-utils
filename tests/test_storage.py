from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from lib.storage import Storage
from lib.storage import StorageError


def create_webinar_info(**kwargs) -> dict[str, str | int]:
    default = {
        "url": "https://...",
        "title": "test",
        "dates": "dates",
        "year": 2023,
    }
    default.update(kwargs)
    return default  # type: ignore


@pytest.fixture(scope="function")
def storage() -> Storage:
    with NamedTemporaryFile() as file:
        return Storage.from_path(Path(file.name))


def test_storage_gives_none_for_uknown_name(storage: Storage) -> None:
    assert storage.get_name_morph('name') is None


def test_storge_gives_name_datv_for_known_name(storage: Storage) -> None:
    storage.set_name_morph('name', 'known-name')
    assert storage.get_name_morph('name') == 'known-name'


def test_storage_raises_if_duplicate_name_set(storage: Storage) -> None:
    storage.set_name_morph('name', 'known-new-name')
    with pytest.raises(StorageError):
        storage.set_name_morph('name', 'known-new-name')


def test_storage_gives_new_id_for_new_webinar(storage: Storage) -> None:
    webinar = create_webinar_info()
    webinar_id = storage.add_webinar(webinar)
    assert webinar_id == '0'


def test_storage_gives_existing_id_for_existing_webinar(
        storage: Storage,
) -> None:
    webinar = create_webinar_info()
    webinar_id = storage.add_webinar(webinar)
    assert storage.add_webinar(webinar) == webinar_id


def test_storage_gives_webinar_by_existing_id(storage: Storage) -> None:
    webinar = create_webinar_info()
    webinar_id = storage.add_webinar(webinar)
    assert storage.get_webinar(webinar_id) == webinar


def test_storage_gives_none_for_unknown_id(storage: Storage) -> None:
    assert storage.get_webinar('99') is None


def test_storage_gives_existing_webinars(storage: Storage) -> None:
    assert len(storage.list_webinars()) == 0
    first = create_webinar_info(url='first')
    second = create_webinar_info(url='second')
    storage.add_webinar(first)
    storage.add_webinar(second)
    webinars = storage.list_webinars()
    assert len(webinars) == 2
    assert first in webinars
    assert second in webinars
