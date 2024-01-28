import re
from dataclasses import dataclass

from gspread import Spreadsheet
from gspread import Worksheet
from gspread import service_account
from gspread.exceptions import APIError

from lib.logging import logger
from lib.participants import Participant

FIX_API_ERROR_MESSAGE = """You have to add permissions to spreadsheet.
Fix APIError:

Share > Get Link > Change > Anyone with link > Editor

"""
PARTICIPANTS = "Form Responses 1"


@dataclass(frozen=True, slots=True)
class Sheet:
    title: str
    date_str: str
    participants: list[Participant]
    document: Spreadsheet
    year: int

    @classmethod
    def from_url(cls, url: str) -> "Sheet":
        document = open_spreadsheet(url)
        participants = get_participants_from_sheet(
            document.worksheet(PARTICIPANTS),
            first_row=1,
        )
        date_str, title = get_webinar_date_and_title(document.title)
        year = get_year_from_participants(participants)
        return cls(
            title=title,
            date_str=date_str,
            participants=participants,
            document=document,
            year=year,
        )


def get_year_from_participants(participants: list[Participant]) -> int:
    for participant in participants:
        if not participant.timestamp:
            continue
        return participant.timestamp.year
    return 2024


def get_participants_from_sheet(
    sheet: Worksheet,
    first_row: int = 0,
) -> list[Participant]:
    participants: list[Participant] = []
    # TODO: по первому столбцу определять какой формат
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
        resp = err._extract_text(err.response)  # pylint: disable=protected-access
        if resp["code"] == 403:
            raise RuntimeError(FIX_API_ERROR_MESSAGE) from err
        raise err


def open_spreadsheet(url: str) -> Spreadsheet:
    document = service_account(
        filename="key.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    ).open_by_url(url)
    ensure_permissions(document)
    return document
