from collections.abc import Iterable
from collections.abc import Sequence
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from functools import cache
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

BOOL2STR: Mapping[bool, str] = {
    True: "TRUE",
    False: "FALSE",
}
STR2BOOL: Mapping[str, bool] = {v: k for k, v in BOOL2STR.items()}


class ApiPermissionError(Exception):
    def __init__(self) -> None:
        message = dedent(
            """You have to add permissions to spreadsheet.
            Fix APIError:

            Share > Get Link > Change > Anyone with link > Editor
            """
        )
        super().__init__(message)


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

    def prepare_emails(
        self,
        rows: Sequence[tuple[str, str, str]],
    ) -> None:
        rows_str: list[tuple[str, str, str, str]] = [
            (row[0], BOOL2STR[False], row[1], row[2]) for row in rows
        ]
        cert_sheet = self.create_cert_sheet(len(rows))
        cert_sheet.append_rows(rows_str)

    def get_emails_ready_to_send(self) -> Iterable[tuple[int, str, str, str]]:
        cert_sheet = self.get_cert_sheet()
        rows = cert_sheet.get_all_values()
        for row_id, row in zip(count(1), rows):
            if STR2BOOL[row[1]]:
                continue
            yield (row_id, row[0], row[2], row[3])

    def mark_as_sent(self, row_id: int) -> None:
        cert_sheet = self.get_cert_sheet()
        cert_sheet.update_cell(row_id, 2, BOOL2STR[True])


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


@cache
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
