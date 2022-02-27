from collections import namedtuple
from datetime import datetime
from typing import Callable

from gspread import Spreadsheet
from gspread import Worksheet

from protocols import ProtoCell
from protocols import ProtoSheet
from protocols import RowsT
from protocols import RowT
from sheets import open_spreadsheet


cell = namedtuple("cell", ["value"])
CreateDocumentT = Callable[[RowsT], Worksheet]
CreateSheetT = Callable[[RowsT], ProtoSheet]

TEST_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1w1m46wDCy3yOyqgI8K0685oIfkMnAEvQyeJjkOMzLCo/edit"
)
TITLE_CELL_NAMES: RowT = [
    'Timestamp',
    'Фамилия:',
    'Имя:',
    'Отчество',
    'Введите ваш телефон:',
    'Введите ваш аккаунт Instagram:',
    'Введите ваш email:',
]


def create_row(
        family: str,
        name: str,
        father: str,
        timestamp: str = None,
        phone: str = '+79161234567',
        instagram: str = '@instagram',
        email: str = 'email@yandex.ru',
) -> RowT:
    timestamp = timestamp or str(datetime.now())
    return [
        timestamp,
        family,
        name,
        father,
        phone,
        instagram,
        email,
    ]


def prepare_sheet(sheet: ProtoSheet, rows: RowsT) -> ProtoSheet:
    sheet.clear()
    sheet.append_row(TITLE_CELL_NAMES)
    sheet.append_rows(rows)
    return sheet


def create_google_document(rows: RowsT) -> Worksheet:
    rows = rows or []
    document = open_spreadsheet(TEST_SHEET_URL)
    for sheet in document.worksheets():
        if sheet.title != "Form Responses 1":
            document.del_worksheet(sheet)
            continue
        prepare_sheet(sheet, rows)
    assert 'Формирование базовых графических представлений' in document.title
    assert '00-99 Месяц' in document.title
    return document


def create_google_sheet(rows: RowsT) -> Spreadsheet:
    return create_google_document(rows).sheet1


class SpreadsheetStub:
    def __init__(self, title: str = 'title') -> None:
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
            row_values.append(None)
        self.row_values(row)[col - 1] = value
        return {}  # mimic gspread


def create_stub_sheet(rows: RowsT) -> ProtoSheet:
    return prepare_sheet(SpreadsheetStub(), rows)
