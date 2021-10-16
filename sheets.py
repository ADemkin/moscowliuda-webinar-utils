from dataclasses import dataclass

from gspread import Worksheet
from gspread import service_account


URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1ROpqWDORLkllt4-QPYiufGg2CRv1oRMxIK35ZU8JnPg/edit?usp=sharing"
)


@dataclass
class Participant:
    name: str
    phone: str
    email: str
    instagram: str


def get_participants_from_sheet(sheet: Worksheet) -> list[Participant]:
    row_index = 5  # first data starts on row #5
    participants: list[Participant] = []
    while True:
        try:
            row_data = sheet.row_values(row_index)
        except IndexError:
            break
        row_index += 1
        # TODO: validate row_data
        if len(row_data) != 4:
            print(f"Invalid row #{row_index-1} with values: {row_data=}")
            continue
        participants.append(Participant(*row_data))
    return participants


document = service_account(
    filename="key.json",
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
).open_by_url(URL)

sheet = document.worksheet('участники')

print(get_participants_from_sheet(sheet))
