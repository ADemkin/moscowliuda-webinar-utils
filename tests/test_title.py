from datetime import date

import pytest

from lib.sheets import InvalidDocumentTitleError
from lib.sheets import _split_title_to_dates_and_title


@pytest.mark.parametrize(
    ("title", "started_at", "finished_at", "webinar_title"),
    [
        (
            "19 - 20 Февраля 2025 Название",
            date(2025, 2, 19),
            date(2025, 2, 20),
            "Название",
        ),
        (
            "31 Мая - 2 Июня 2025 Название из 4 слов",
            date(2025, 5, 31),
            date(2025, 6, 2),
            "Название из 4 слов",
        ),
        (
            "25 Июля - 1 Августа 2025 Название (Responses)",
            date(2025, 7, 25),
            date(2025, 8, 1),
            "Название",
        ),
    ],
)
def test_split_title_to_dates_and_title(
    title: str,
    started_at: date,
    finished_at: date,
    webinar_title: str,
) -> None:
    assert _split_title_to_dates_and_title(title) == (started_at, finished_at, webinar_title)


@pytest.mark.parametrize(
    "title",
    [
        "unknown format",
        "19-20 Февраля 2025 без пробела между датами",
        "19 - 20 Февраля без года",
        "19 Февраля - 20 Февраля без года",
        "19 - 20 Мумраля 2025 неизвестный месяц",
        "19 Мумраля - 20 Мумраля 2025 неизвестный месяц",
    ],
)
def test_split_title_to_dates_and_title_raises_if_unknown_format(title: str) -> None:
    with pytest.raises(InvalidDocumentTitleError):
        _split_title_to_dates_and_title(title)
