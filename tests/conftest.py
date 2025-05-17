from typing import Any

import pytest

from lib.clients.db import DB
from tests.common import CreateDocumentT
from tests.common import CreateSheetT
from tests.common import create_google_document
from tests.common import create_google_sheet
from tests.common import create_stub_document
from tests.common import create_stub_sheet


@pytest.fixture(
    params=[
        create_google_document,
        create_stub_document,
    ],
)
def create_document(request: Any) -> CreateDocumentT:
    return request.param


@pytest.fixture(params=[create_google_sheet, create_stub_sheet])
def create_sheet(request: Any) -> CreateSheetT:
    return request.param


@pytest.fixture(scope="session")
def db(tmp_path_factory) -> DB:
    tmp_path = tmp_path_factory.mktemp("data")
    db_path = tmp_path / "test.db"
    return DB(path=db_path)
