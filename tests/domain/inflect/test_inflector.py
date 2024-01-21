import pytest

from lib.domain.inflect.inflector import Inflector


@pytest.fixture
def inflector() -> Inflector:
    return Inflector()


@pytest.mark.parametrize(
    "name,name_datv_expected",
    [
        ("Антон", "Антону"),
        ("Людмила", "Людмиле"),
        ("Андреевна", "Андреевне"),
        ("Антонович", "Антоновичу"),
        ("Андреевич", "Андреевичу"),
        ("Мельникова", "Мельниковой"),
        ("Мельников", "Мельникову"),
        ("Дёмкин", "Дёмкину"),
        ("Дёмкина", "Дёмкиной"),
        ("Владимирович", "Владимировичу"),
        ("Владимировна", "Владимировне"),
    ],
)
def test_inflector_inflect_datv_gives_inflected_datv_form(
    inflector: Inflector,
    name: str,
    name_datv_expected: str,
) -> None:
    assert inflector.inflect_datv(name) == name_datv_expected
