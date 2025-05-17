from typing import Any

import pytest

from lib.clients.db import DB
from tests.common import CreateDocumentT
from tests.common import create_google_document
from tests.common import create_stub_document


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Include real google sheets tests",
    )


@pytest.fixture(
    params=[
        create_google_document,
        create_stub_document,
    ],
)
def create_document(request: Any) -> CreateDocumentT:
    if request.param == create_google_document and not request.config.getoption("--live"):
        pytest.skip("Skipping live tests. Use --live to run them.")
    return request.param


@pytest.fixture(scope="session")
def db(tmp_path_factory) -> DB:
    tmp_path = tmp_path_factory.mktemp("data")
    db_path = tmp_path / "test.db"
    return DB(path=db_path)
