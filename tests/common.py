from contextlib import suppress
from os import urandom
from typing import Callable
from typing import NamedTuple

import pytest
from faker import Faker
from gspread.exceptions import WorksheetNotFound

from lib.sheets import open_spreadsheet
from lib.types import ProtoDocument
from lib.types import ProtoSheet
from lib.types import RowsT
from lib.types import RowT


class Cell(NamedTuple):
    value: str | None


CreateDocumentT = Callable[[RowsT], ProtoDocument]
CreateSheetT = Callable[[RowsT], ProtoSheet]

# fmt: off
TEST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1w1m46wDCy3yOyqgI8K0685oIfkMnAEvQyeJjkOMzLCo/edit"
# fmt: on
TITLE_CELL_NAMES: RowT = [
    "Timestamp",
    "Фамилия:",
    "Имя:",
    "Отчество",
    "Введите ваш телефон:",
    "[deprecated]",
    "Email address",
]

DEFAULT_TITLE = "01 - 31 Января 2025 Test Webinar (Responses)"

ru_faker = Faker("ru_RU")
international_faker = Faker()


class SpreadsheetStub:
    def __init__(self, title: str = "title") -> None:
        self._rows: RowsT = []
        self.title = title

    def clear(self) -> None:
        self._rows = []

    def append_row(self, row: RowT) -> None:
        self._rows.append(list(row))

    def append_rows(self, rows: RowsT) -> None:
        self._rows.extend(list(r) for r in rows)

    def row_values(self, row: int) -> RowT:
        return self._rows[row - 1]

    def cell(self, row: int, col: int) -> Cell:
        value = None
        with suppress(IndexError):
            value = self._rows[row - 1][col - 1]
        return Cell(value)

    def update_cell(self, row: int, col: int, value: str) -> dict[str, str]:
        col_index = col - 1
        row_values = self._rows[row - 1]
        while len(row_values) <= col_index:
            row_values.append("")
        self.row_values(row)[col - 1] = value
        return {}  # mimic gspread

    def get_all_values(self) -> RowsT:
        return self._rows


class WorksheetStub:
    def __init__(self) -> None:
        self._title = ""
        self._worksheets: list[SpreadsheetStub] = []
        self.add_worksheet("Form Responses 1", 100, 100)  # can not be deleted

    def update_title(self, title: str) -> None:
        self._title = title

    def worksheets(self) -> list[SpreadsheetStub]:
        return self._worksheets

    def worksheet(self, title: str) -> SpreadsheetStub:
        for sheet in self._worksheets:
            if sheet.title == title:
                return sheet
        raise WorksheetNotFound

    @property
    def title(self) -> str:
        return self._title

    def add_worksheet(
        self,
        title: str,
        rows: int,  # noqa: ARG002
        cols: int,  # noqa: ARG002
        index: int | None = None,  # noqa: ARG002
    ) -> SpreadsheetStub:
        sheet = SpreadsheetStub(title)
        self._worksheets.append(sheet)
        return sheet

    def del_worksheet(self, sheet: ProtoSheet) -> None:
        title = sheet.title
        for i, _sheet in enumerate(self._worksheets):
            if _sheet.title == title:
                self._worksheets.pop(i)
                return
        raise WorksheetNotFound


def prepare_sheet(sheet: ProtoSheet, rows: RowsT) -> ProtoSheet:
    sheet.clear()
    sheet.append_row(TITLE_CELL_NAMES)
    sheet.append_rows(rows)
    return sheet


def prepare_document(document: ProtoDocument, rows: RowsT) -> ProtoDocument:
    document.update_title(DEFAULT_TITLE)
    for sheet in document.worksheets():
        if sheet.title != "Form Responses 1":
            document.del_worksheet(sheet)
            continue
        prepare_sheet(sheet, rows)
    return document


def create_google_document(rows: RowsT) -> ProtoDocument:
    sheet = open_spreadsheet(TEST_SHEET_URL)
    return prepare_document(sheet, rows)  # type: ignore[arg-type]


def create_stub_document(rows: RowsT) -> WorksheetStub:
    return prepare_document(WorksheetStub(), rows)  # type: ignore[arg-type,return-value]


def create_google_sheet(rows: RowsT) -> ProtoSheet:
    return create_google_document(rows).worksheet("Form Responses 1")


def create_stub_sheet(rows: RowsT) -> SpreadsheetStub:
    return prepare_sheet(SpreadsheetStub(), rows)  # type: ignore[arg-type,return-value]


def randstr() -> str:
    return urandom(8).hex()


def randint() -> int:
    return int.from_bytes(urandom(4), byteorder="big")
