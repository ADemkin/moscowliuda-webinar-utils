import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from http import HTTPStatus

from gspread import Spreadsheet
from gspread import Worksheet
from gspread import service_account
from gspread.exceptions import APIError

from lib.const import NAME2MONTH
from lib.logging import logger
from lib.participants import Participant

PARTICIPANTS = "Form Responses 1"

RE_DATE = r"(\d{1,2})"
RE_MONTH = r"(\w+)"
RE_YEAR = r"(\d{4})"
RE_TITLE = r"(.*)"
SAME_MONTH_RE = re.compile(rf"{RE_DATE} - {RE_DATE} {RE_MONTH} {RE_YEAR} {RE_TITLE}")
RE_DATE_MONTH = rf"{RE_DATE} {RE_MONTH}"
DIFF_MONTH_RE = re.compile(rf"{RE_DATE_MONTH} - {RE_DATE_MONTH} {RE_YEAR} {RE_TITLE}")


class ApiPermissionError(Exception):
    def __init__(self) -> None:
        message = """You have to add permissions to spreadsheet.
Fix APIError:

Share > Get Link > Change > Anyone with link > Editor
"""
        super().__init__(message)


class InvalidDocumentTitleError(Exception):
    def __init__(self, title: str) -> None:
        message = f"""Невереный формат названия документа: {title!r}
Ожидается формат:
19-20 Февраля 2025 Формирование базовых грамматических представлений\n
31 Мая - 2 Июня 2025 Формирование базовых грамматических представлений\n
        """
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class Sheet:
    document_title: str
    participants: Iterable[Participant]
    document: Spreadsheet

    @classmethod
    def from_url(cls, url: str) -> "Sheet":
        document = open_spreadsheet(url)
        participants = get_participants_from_sheet(
            document.worksheet(PARTICIPANTS),
            first_row=1,
        )
        return cls(
            document_title=document.title,
            participants=participants,
            document=document,
        )

    def get_started_at(self) -> date:
        started_at, _, _ = _split_title_to_dates_and_title(self.document_title)
        return started_at

    def get_finished_at(self) -> date:
        _, finished_at, _ = _split_title_to_dates_and_title(self.document_title)
        return finished_at

    def get_webinar_title(self) -> str:
        _, _, title = _split_title_to_dates_and_title(self.document_title)
        return title.lower()


def get_participants_from_sheet(
    sheet: Worksheet,
    first_row: int = 0,
) -> Iterable[Participant]:
    participants: list[Participant] = []
    # TODO: по первому столбцу определять какой формат
    for row in sheet.get_all_values()[first_row:]:
        try:
            participant = Participant.from_row_v2(row)
        except Exception as err:  # noqa: BLE001
            logger.error(err)
            continue
        participants.append(participant)
    return participants


def _split_title_to_dates_and_title(title: str) -> tuple[date, date, str]:
    """Достать из названия документа даты проведения и название вебинара.

    Возможные форматы:
    19 - 20 Февраля 2025 Формирование базовых грамматических представлений (Responses)
    31 Мая - 2 Июня 2025 Формирование базовых грамматических представлений (Responses)

    Возвращает:
    - дату начала
    - дату окончания
    - название вебинара строкой
    """

    def name2month(name: str) -> int:
        try:
            return NAME2MONTH[name.lower()]
        except KeyError as err:
            raise InvalidDocumentTitleError(title) from err

    title = title.removesuffix(" (Responses)")
    if match := SAME_MONTH_RE.match(title):
        start_day, end_day, month, year, title = match.groups()
        started_at = date(
            year=int(year),
            month=name2month(month),
            day=int(start_day),
        )
        finished_at = date(
            year=int(year),
            month=name2month(month),
            day=int(end_day),
        )
        return started_at, finished_at, title
    if match := DIFF_MONTH_RE.match(title):  # type: ignore[unreachable]
        start_day, start_month, end_day, end_month, year, title = match.groups()
        started_at = date(
            year=int(year),
            month=name2month(start_month),
            day=int(start_day),
        )
        finished_at = date(
            year=int(year),
            month=name2month(end_month),
            day=int(end_day),
        )
        return started_at, finished_at, title
    raise InvalidDocumentTitleError(title)


def ensure_permissions(document: Spreadsheet) -> None:
    try:
        document.worksheets()
    except APIError as err:
        if err.code == HTTPStatus.FORBIDDEN:
            raise ApiPermissionError from err
        raise


def open_spreadsheet(url: str) -> Spreadsheet:
    document = service_account(
        filename="key.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    ).open_by_url(url)
    ensure_permissions(document)
    return document
