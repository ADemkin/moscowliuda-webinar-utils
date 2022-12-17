from storage import Storage, StorageError
import pytest


@pytest.fixture
def storage() -> Storage:
    return Storage.temporary()


def test_storage_gives_none_for_uknown_name(storage: Storage) -> None:
    assert storage.get_name_morph('name') is None


def test_storge_gives_name_datv_for_known_name(storage: Storage) -> None:
    storage.set_name_morph('name', 'known-name')
    assert storage.get_name_morph('name') == 'known-name'


def test_storage_raises_if_duplicate_name_set(storage: Storage) -> None:
    storage.set_name_morph('name', 'known-name')
    with pytest.raises(StorageError):
        storage.set_name_morph('name', 'known-name')
