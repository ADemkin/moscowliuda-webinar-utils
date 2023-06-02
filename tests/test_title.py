import pytest

from lib.sheets import get_webinar_date_and_title


@pytest.mark.parametrize("date,name", [
    ("10-20 Января", "Название вебинара"),
    ("1-2 Февраля", "Название"),
    ("2 - 5 Февраля", "Практика Запуска Речи"),
    ("20 - 25 Февраля", "Название"),
    ("1-99 Марта", "Длинное Название из нескольких слов"),
    ("1-99 Марта", "Длинное Название из нескольких слов"),
    ("28 Апреля - 1 Мая", "Название"),
    ("28 Апреля - 1 Мая", "Длинное Название из нескольких слов"),
])
def test_gives_date_and_title_if_given_correct_title(
        date: str,
        name: str
) -> None:
    title = f" {date} {name} (Responses) "
    assert get_webinar_date_and_title(title) == (date, name)


@pytest.mark.parametrize("title", [
    "",
    "123",
    "10 февраля название",
    "12-12 месяц",
    "название",
])
def test_if_given_incorrect_title_then_raises(title: str) -> None:
    with pytest.raises(RuntimeError):
        get_webinar_date_and_title(title)
