import re
from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from enum import unique
from functools import cached_property
from functools import lru_cache
from http import HTTPStatus
from itertools import count
from textwrap import dedent
from typing import Self

from gspread import Spreadsheet
from gspread import Worksheet
from gspread import service_account
from gspread.exceptions import APIError
from gspread.exceptions import WorksheetNotFound

from lib.const import NAME2MONTH
from lib.domain.webinar.enums import WebinarTitle
from lib.logging import logger
from lib.participants import Participant
from lib.utils import text_to_date_range_and_title

PARTICIPANTS_SHEET_NAME = "Form Responses 1"
CERTIFICATES_SHEET_NAME = "mailing"


class ApiPermissionError(Exception):
    def __init__(self) -> None:
        message = dedent(
            """You have to add permissions to spreadsheet.
            Fix APIError:

            Share > Get Link > Change > Anyone with link > Editor
            """
        )
        super().__init__(message)


@unique
class IsSent(StrEnum):
    TRUE = "TRUE"
    FALSE = "FALSE"

    def __bool__(self) -> bool:
        return self == IsSent.TRUE

    @classmethod
    def from_bool(cls, value: bool) -> "IsSent":  # noqa: FBT001
        return cls.TRUE if value else cls.FALSE


@dataclass(frozen=True, slots=True)
class Sheet:
    document: Spreadsheet
    mailing_headers: tuple[str, str, str, str] = ("fio", "is_sent", "email", "custom_text")

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(document=open_spreadsheet(url))

    def get_participants(self) -> Iterable[Participant]:
        return get_participants_from_sheet(
            self.document.worksheet(PARTICIPANTS_SHEET_NAME),
            first_row=1,
        )

    @property
    def document_title(self) -> str:
        return self.document.title

    def get_started_at(self) -> date:
        started_at, _, _ = _split_title_to_dates_and_title(self.document_title)
        return started_at

    def get_finished_at(self) -> date:
        _, finished_at, _ = _split_title_to_dates_and_title(self.document_title)
        return finished_at

    def get_webinar_title(self) -> WebinarTitle:
        _, _, title = _split_title_to_dates_and_title(self.document_title)
        return WebinarTitle.from_text(title)

    def create_cert_sheet(self, size: int) -> Worksheet:
        logger.info("creating certificates sheet")
        return self.document.add_worksheet(
            title=CERTIFICATES_SHEET_NAME,
            rows=size,
            cols=len(self.mailing_headers),
        )

    def get_cert_sheet(self) -> Worksheet:
        return self.document.worksheet(CERTIFICATES_SHEET_NAME)

    def prepare_mailing(
        self,
        rows: Sequence[tuple[str, bool, str, str]],
    ) -> None:
        rows_str: list[tuple[str, str, str, str]] = [
            (row[0], str(IsSent.from_bool(row[1])), row[2], row[3]) for row in rows
        ]
        cert_sheet = self.create_cert_sheet(len(rows))
        cert_sheet.clear()
        cert_sheet.append_rows(rows_str)

    def get_mailing_rows(self) -> Iterable[tuple[int, str, bool, str, str]]:
        cert_sheet = self.get_cert_sheet()
        rows = cert_sheet.get_all_values()
        for row_id, row in zip(count(1), rows):
            yield (row_id, row[0], bool(IsSent(row[1])), row[2], row[3])

    def mark_as_sent(self, row_id: int) -> None:
        cert_sheet = self.get_cert_sheet()
        cert_sheet.update_cell(row_id, 2, str(IsSent.TRUE))


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


@lru_cache
def _split_title_to_dates_and_title(title: str) -> tuple[date, date, str]:
    """Достать из названия документа даты проведения и название вебинара.

    Возможные форматы:
    19 - 20 Февраля 2025 Формирование базовых грамматических представлений (Responses)
    31 Мая - 2 Июня 2025 Формирование базовых грамматических представлений (Responses)

    Рейзит:
    - InvalidTitleError если не получилось распарсить название документа

    Возвращает:
    - дату начала
    - дату окончания
    - название вебинара строкой
    """
    title = title.removesuffix(" (Responses)")
    return text_to_date_range_and_title(title)


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
