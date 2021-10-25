from typing import Callable
from dataclasses import dataclass

from gspread import service_account
from gspread import Worksheet
from loguru import logger

from word_morph import get_fio_in_given_form
from word_morph import WordMorphError


URL = "https://docs.google.com/spreadsheets/d/1ROpqWDORLkllt4-QPYiufGg2CRv1oRMxIK35ZU8JnPg/edit?usp=sharing"


@dataclass
class Participant:
    name: str
    phone: str
    email: str
    instagram: str

    def name_in_given_form(self) -> str:
        try:
            return get_fio_in_given_form(self.name)
        except WordMorphError as err:
            logger.error(err)
            return ''

def sanitize_temporary_row_data(row_data: list[str]) -> list[str]:
    if len(row_data) == 3:
        logger.debug(f"no instagram account for {row_data[0]}")
        row_data.append('')
    if len(row_data) != 4:
        logger.error(f"Invalid row with values: {row_data=}")
    # sanitize name
    row_data[0] = row_data[0].strip()
    # sanitize phone
    row_data[1] = row_data[1].strip().replace(' ', '')
    # sanitize email
    row_data[2] = row_data[2].strip()
    # sanitize instagram
    row_data[3] = row_data[3].strip()
    return row_data


def get_participants_from_sheet(
        sheet: Worksheet,
        row_index: int = 0,
        sanitize_row: Callable = lambda x: x,
) -> list[Participant]:
    participants: list[Participant] = []
    while True:
        try:
            row_data = sheet.row_values(row_index)
        except IndexError:
            break
        row_index += 1
        try:
            row_data = sanitize_row(row_data)
        except Exception as err:
            logger.error(err)
            continue
        participants.append(Participant(*row_data))
    return participants


def get_webinar_date_from_sheet(sheet: Worksheet) -> str:
    return sheet.row_values(1)[0]


def get_webinar_topic_from_sheet(sheet: Worksheet) -> str:
    return sheet.row_values(2)[0]


document = service_account(
    filename="key.json",
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
).open_by_url(URL)

sheet = document.worksheet('участники')

print(get_webinar_topic_from_sheet(sheet))
print(get_webinar_date_from_sheet(sheet))
for participant in get_participants_from_sheet(
    sheet,
    row_index=5,
    sanitize_row=sanitize_temporary_row_data,
):
    print(participant.name, participant.phone, participant.email)
