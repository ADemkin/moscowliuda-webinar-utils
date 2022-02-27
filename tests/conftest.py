from typing import Any

import pytest

from tests.common import create_google_document
from tests.common import create_google_sheet
from tests.common import create_stub_sheet
from tests.common import CreateDocumentT
from tests.common import CreateSheetT


@pytest.fixture(params=[
    create_google_document,
])
def create_document(request: Any) -> CreateDocumentT:
    return request.param


@pytest.fixture(params=[
    create_google_sheet,
    create_stub_sheet
])
def create_sheet(request: Any) -> CreateSheetT:
    return request.param
