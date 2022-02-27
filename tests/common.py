from datetime import datetime

from gspread import Worksheet

from sheets import open_spreadsheet

TEST_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1w1m46wDCy3yOyqgI8K0685oIfkMnAEvQyeJjkOMzLCo/edit"
)
TITLE_CELL_NAMES = [
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
) -> list[str]:
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


def create_test_sheet(rows: list[list[str]] = None) -> Worksheet:
    rows = rows or []
    document = open_spreadsheet(TEST_SHEET_URL)
    for sheet in document.worksheets():
        if sheet.title != "Form Responses 1":
            document.del_worksheet(sheet)
            continue
        sheet.clear()
        sheet.append_row(TITLE_CELL_NAMES)
        sheet.append_rows(rows)
    assert 'Формирование базовых графических представлений' in document.title
    assert '00-99 Месяц' in document.title
    return document
