import re

from gspread import service_account
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import APIError
from loguru import logger

from participants import Participant


FIX_API_ERROR_MESSAGE = """You have to add permissions to spreadsheet.
Fix APIError:

Share > Get Link > Change > Anyone with link > Editor

"""


def get_participants_from_sheet(
        sheet: Worksheet,
        first_row: int = 0,
) -> list[Participant]:
    participants: list[Participant] = []
    for row in sheet.get_all_values()[first_row:]:
        try:
            participants.append(Participant.from_row(row))
        except Exception as err:
            logger.error(err)
            continue
    return participants


def get_webinar_date_and_title(document: Spreadsheet) -> tuple[str, str]:
    title = document.title.rstrip(" (Responses)")
    groups = re.match(r"(\d{1,2}\-\d{1,2} \w+) (.*)", title).groups()
    if len(groups) != 2:
        raise RuntimeError(
            "Spreadsheet title does not contain date and webinar title. "
            "Use format: "
            "'19-20 Февраля Формирование базовых графических представлений'"
        )
    return groups


def ensure_permissions(document: Spreadsheet) -> None:
    try:
        document.worksheets()
    except APIError as err:
        if err._extract_text(err.response)['code'] == 403:
            raise RuntimeError(FIX_API_ERROR_MESSAGE) from err


def open_spreadsheet(url: str) -> Spreadsheet:
    document = service_account(
        filename="key.json",
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
    ).open_by_url(url)
    ensure_permissions(document)
    return document
