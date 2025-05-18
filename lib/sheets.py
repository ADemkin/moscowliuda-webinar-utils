import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from http import HTTPStatus
from typing import Self

from gspread import Spreadsheet
from gspread import Worksheet
from gspread import service_account
from gspread.exceptions import APIError

from lib.const import NAME2MONTH
from lib.domain.webinar.enums import WebinarTitle
from lib.logging import logger
from lib.participants import Participant
from lib.utils import text_to_date_range_and_title

PARTICIPANTS = "Form Responses 1"


class ApiPermissionError(Exception):
    def __init__(self) -> None:
        message = """You have to add permissions to spreadsheet.
Fix APIError:

Share > Get Link > Change > Anyone with link > Editor
"""
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class Sheet:
    document_title: str
    participants: Iterable[Participant]
    document: Spreadsheet

    @classmethod
    def from_url(cls, url: str) -> Self:
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

    def get_webinar_title(self) -> WebinarTitle:
        _, _, title = _split_title_to_dates_and_title(self.document_title)
        return WebinarTitle.from_text(title)


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
