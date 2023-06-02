import re

from gspread import service_account
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import APIError
from loguru import logger

from lib.participants import Participant

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
            participants.append(Participant.from_row_v2(row))
        except Exception as err:
            logger.error(err)
            continue
    return participants


def get_webinar_date_and_title(title: str) -> tuple[str, str]:
    title = title.strip().rstrip(" (Responses)")
    match = re.match(r"(\d{1,2}\s?\-\s?\d{1,2} \w+) (.*)", title)
    match = match or re.match(r"(\d{1,2} \w+\s-\s\d{1,2} \w+) (.*)", title)
    if match:
        if groups := match.groups():
            if len(groups) == 2:
                return str(groups[0].strip()), str(groups[1].strip())
    raise RuntimeError(
        f"Title does not contain date and webinar title: {title!r}\n"
        "Use format:\n"
        "'19-20 Февраля Формирование базовых грамматических представлений'\n"
        "'31 Мая - 2 Июня Формирование базовых грамматических представлений'\n"
    )


def ensure_permissions(document: Spreadsheet) -> None:
    try:
        document.worksheets()
    except APIError as err:
        if err._extract_text(err.response)["code"] == 403:
            raise RuntimeError(FIX_API_ERROR_MESSAGE) from err


def open_spreadsheet(url: str) -> Spreadsheet:
    document = service_account(
        filename="key.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    ).open_by_url(url)
    ensure_permissions(document)
    return document
