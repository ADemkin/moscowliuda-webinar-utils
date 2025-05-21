import pytest

from lib.utils import normalize_phone_number


@pytest.mark.parametrize(
    ("phone_raw", "expected"),
    [
        ("+79161234567", "+79161234567"),
        ("89161234567", "+79161234567"),
        ("+379161234567", "+379161234567"),
        ("+7(916)123-45-67", "+79161234567"),
        ("+7 916 123 45 67", "+79161234567"),
        ("", ""),
    ],
)
def test_normalize_phone_number(phone_raw: str, expected: str) -> None:
    assert normalize_phone_number(phone_raw) == expected
