from pathlib import Path
import json

import pytest

from lib.storage import WebinarStorage
from lib.factory import WebinarTitles


@pytest.fixture(name='storage')
def storage_fixture(tmp_path: Path) -> WebinarStorage:
    file_path = tmp_path / 'storage.json'
    with open(file_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps([]))
    storage = WebinarStorage(file_path)
    return storage


def test_empty_storage_gives_empty_list(storage: WebinarStorage) -> None:
    assert storage.get_all_webinars() == []


def test_if_webinar_not_found_then_gives_none(storage: WebinarStorage) -> None:
    assert storage.get_webinar_by_id(-1) is None


def test_if_webinar_exists_then_gives_webinar(storage: WebinarStorage) -> None:
    url = 'some-url'
    title = WebinarTitles.TEST
    webinar_id = storage.add_webinar(url, title)
    webinar = storage.get_webinar_by_id(webinar_id)
    assert webinar
    assert webinar.url == url
    assert webinar.title == title


def test_if_webinar_exists_then_it_appears_in_all(storage: WebinarStorage) -> None:
    url = 'some-url'
    title = WebinarTitles.TEST
    webinar = storage.get_webinar_by_id(storage.add_webinar(url, title))
    all_webinars = storage.get_all_webinars()
    assert webinar in all_webinars
