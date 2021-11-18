from gspread import service_account
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from loguru import logger

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


def get_webinar_date_from_sheet(sheet: Worksheet) -> str:
    return sheet.row_values(1)[0]


def get_webinar_topic_from_sheet(sheet: Worksheet) -> str:
    return sheet.row_values(2)[0]


def create_spreadsheet(url: str = URL) -> Spreadsheet:
    """Create spreadsheet object from url

    Fix APIError: Go to Share > Get Link > Change > Anyone with link > Editor
    """
    return service_account(
        filename="key.json",
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
    ).open_by_url(url)


