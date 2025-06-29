from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Callable

import pytest

from lib.clients.db import DB
from lib.types import RowT
from tests.common import CreateDocumentT
from tests.common import create_google_document
from tests.common import create_stub_document
from tests.common import international_faker
from tests.common import ru_faker


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
    ids=["google", "stub"],
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


@pytest.fixture
def create_row() -> Callable[..., RowT]:
    def _create_row(
        family: str | None = None,
        name: str | None = None,
        father: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> RowT:
        timestamp = datetime.now(timezone.utc).isoformat()
        family = family or ru_faker.last_name_female()
        name = name or ru_faker.first_name()
        father = father or ru_faker.middle_name()
        phone = phone or international_faker.phone_number()
        email = email or international_faker.email()
        return [
            timestamp,
            email,
            family,
            name,
            father,
            phone,
        ]

    return _create_row
