from typing import Any

import pytest

from lib.word_morph import offline_morph
from tests.common import CreateDocumentT
from tests.common import CreateSheetT
from tests.common import MorpherT
from tests.common import create_google_document
from tests.common import create_google_sheet
from tests.common import create_stub_document
from tests.common import create_stub_sheet


@pytest.fixture(
    params=[
        create_google_document,
        create_stub_document,
    ]
)
def create_document(request: Any) -> CreateDocumentT:
    return request.param


@pytest.fixture(params=[create_google_sheet, create_stub_sheet])
def create_sheet(request: Any) -> CreateSheetT:
    return request.param


@pytest.fixture(
    params=[
        offline_morph,
    ]
)
def morpher(request: Any) -> MorpherT:
    return request.param
