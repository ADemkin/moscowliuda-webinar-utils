from collections import namedtuple
from datetime import datetime
from functools import wraps
from os import urandom
from typing import Any
from typing import Callable

import pytest
from google.auth.exceptions import TransportError
from gspread.exceptions import WorksheetNotFound

from lib.domain.webinar.models import Account
from lib.domain.webinar.models import AccountId
from lib.participants import GOOGLE_TIMESTAMP_FORMAT
from lib.protocols import ProtoCell
from lib.protocols import ProtoDocument
from lib.protocols import ProtoSheet
from lib.protocols import RowsT
from lib.protocols import RowT
from lib.sheets import open_spreadsheet

cell = namedtuple("cell", ["value"])

CreateDocumentT = Callable[[RowsT], ProtoDocument]
CreateSheetT = Callable[[RowsT], ProtoSheet]

# fmt: off
TEST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1w1m46wDCy3yOyqgI8K0685oIfkMnAEvQyeJjkOMzLCo/edit"  # noqa: E501
# fmt: on
TITLE_CELL_NAMES: RowT = [
    "Timestamp",
    "Фамилия:",
    "Имя:",
    "Отчество",
    "Введите ваш телефон:",
    "Email address",
]

DEFAULT_TITLE = "01 - 31 Января 2025 Test Webinar (Responses)"


def create_row(
    family: str,
    name: str,
    father: str,
    phone: str = "+79161234567",
    email: str = "email@yandex.ru",
) -> RowT:
    timestamp = datetime.strftime(datetime.now(), GOOGLE_TIMESTAMP_FORMAT)
    return [
        timestamp,
        family,
        name,
        father,
        phone,
        "",
        email,
    ]


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
    return prepare_document(open_spreadsheet(TEST_SHEET_URL), rows)


def create_stub_document(rows: RowsT) -> ProtoDocument:
    return prepare_document(WorksheetStub(), rows)


def create_google_sheet(rows: RowsT) -> ProtoSheet:
    return create_google_document(rows).worksheet("Form Responses 1")


class SpreadsheetStub:
    def __init__(self, title: str = "title") -> None:
        self._rows: RowsT = []
        self.title = title

    def clear(self) -> None:
        self._rows = []

    def append_row(self, row: RowT) -> None:
        self._rows.append(row)

    def append_rows(self, rows: RowsT) -> None:
        self._rows.extend(rows)

    def row_values(self, row: int) -> RowT:
        return self._rows[row - 1]

    def cell(self, row: int, col: int) -> ProtoCell:
        try:
            return cell(self._rows[row][col - 1])
        except IndexError:
            return cell(None)

    def update_cell(self, row: int, col: int, value: str) -> dict:
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
        self._worksheets: list[ProtoSheet] = []
        self.add_worksheet("Form Responses 1")  # can not be deleted

    def update_title(self, title: str) -> None:
        self._title = title

    def worksheets(self) -> list[ProtoSheet]:
        return self._worksheets

    def worksheet(self, title: str) -> ProtoSheet:
        for sheet in self._worksheets:
            if sheet.title == title:
                return sheet
        raise WorksheetNotFound()

    @property
    def title(self) -> str:
        return self._title

    def add_worksheet(
        self,
        title: str,
        rows: int = 100,  # pylint: disable=unused-argument
        cols: int = 100,  # pylint: disable=unused-argument
    ) -> ProtoSheet:
        sheet = SpreadsheetStub(title)
        self._worksheets.append(sheet)
        return sheet

    def del_worksheet(self, sheet: ProtoSheet) -> None:
        title = sheet.title
        for i, _sheet in enumerate(self._worksheets):
            if _sheet.title == title:
                self._worksheets.pop(i)
                return
        raise WorksheetNotFound()


def create_stub_sheet(rows: RowsT) -> ProtoSheet:
    return prepare_sheet(SpreadsheetStub(), rows)


def skipif(exception: BaseException, reason: str) -> Any:
    """Helper to skip some tests if certain exception is raised.

    Main goal is to skip online integration tests if network is down.
    """

    def decorator(func: Callable) -> Any:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:  # pylint: disable=inconsistent-return-statements
            try:
                return func(*args, **kwargs)
            except exception:  # type: ignore
                pytest.skip(reason)

        return wrapper

    return decorator


skip_if_no_network = skipif(TransportError, "Network is down")


def randstr() -> str:
    return urandom(8).hex()


def randint() -> int:
    return int.from_bytes(urandom(4), byteorder="big")


def make_account(
    *,
    account_id: int | None = None,
    registered_at: datetime | None = None,
    family_name: str | None = None,
    name: str | None = None,
    father_name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    webinar_id: int | None = None,
) -> Account:
    return Account(
        id=AccountId(account_id or randint()),
        registered_at=registered_at or datetime.now(),
        family_name=family_name or randstr(),
        name=name or randstr(),
        father_name=father_name or randstr(),
        phone=phone or randstr(),
        email=email or randstr(),
        webinar_id=webinar_id or randint(),
    )
