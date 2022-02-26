import pytest

from tests.common import create_test_sheet


@pytest.fixture(params=[create_test_sheet])
def create_sheet(request: any) -> any:
    return request.param
