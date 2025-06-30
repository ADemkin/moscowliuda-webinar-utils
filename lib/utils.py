import re
from datetime import date
from textwrap import dedent

from lib.const import MONTH2NAME
from lib.const import NAME2MONTH
from lib.const import Month

_RE_DAY = r"(\d{1,2})"
_RE_MONTH = r"(\w+)"
_RE_YEAR = r"(\d{4})"
_RE_TITLE = r"(.*)"
_RE_DAY_MONTH = rf"{_RE_DAY} {_RE_MONTH}"
_RE_SAME_MONTH = re.compile(
    rf"{_RE_DAY} - {_RE_DAY} {_RE_MONTH} {_RE_YEAR} {_RE_TITLE}",
)
_RE_DIFFERENT_MONTH = re.compile(
    rf"{_RE_DAY_MONTH} - {_RE_DAY_MONTH} {_RE_YEAR} {_RE_TITLE}",
)


def date_range_to_text(started_at: date, finished_at: date) -> str:
    start_day = started_at.day
    finish_day = finished_at.day
    finish_month = MONTH2NAME[Month(finished_at.month)]
    text = ""
    if finished_at.month == started_at.month:
        text += f"{start_day} - {finish_day} {finish_month}"
    else:
        start_month = MONTH2NAME[Month(started_at.month)]
        text += f"{start_day} {start_month} - {finish_day} {finish_month}"
    text += f"\n{finished_at.year} г."
    return text


class InvalidTitleError(Exception):
    def __init__(self, title: str) -> None:
        message = dedent(
            f"""Неверный формат названия документа: {title!r}
            Ожидается формат:
            19-20 Февраля 2025 Формирование базовых грамматических представлений\n
            31 Мая - 2 Июня 2025 Формирование базовых грамматических представлений\n
            """
        )
        super().__init__(message)


def text_to_date_range_and_title(text: str) -> tuple[date, date, str]:
    def get_month_number_by_name(name: str) -> int:
        try:
            return NAME2MONTH[name.lower()]
        except KeyError as err:
            raise InvalidTitleError(text) from err

    if (match := _RE_SAME_MONTH.match(text)) is not None:
        start_day, end_day, month, year, title = match.groups()
        started_at = date(
            year=int(year),
            month=get_month_number_by_name(month),
            day=int(start_day),
        )
        finished_at = date(
            year=int(year),
            month=get_month_number_by_name(month),
            day=int(end_day),
        )
    elif (match := _RE_DIFFERENT_MONTH.match(text)) is not None:
        start_day, start_month, end_day, end_month, year, title = match.groups()
        started_at = date(
            year=int(year),
            month=get_month_number_by_name(start_month),
            day=int(start_day),
        )
        finished_at = date(
            year=int(year),
            month=get_month_number_by_name(end_month),
            day=int(end_day),
        )
    else:
        raise InvalidTitleError(text)
    return started_at, finished_at, title


def normalize_phone_number(number: str) -> str:
    number = "".join(c for c in number if c.isdigit())
    if number.startswith("8"):
        number = f"7{number[1:]}"
    return f"+{number}" if number else ""


def normalize_email(email: str) -> str:
    return email.lower()
