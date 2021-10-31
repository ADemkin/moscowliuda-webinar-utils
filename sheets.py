from dataclasses import dataclass

from gspread import service_account
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import APIError
from gspread.exceptions import WorksheetNotFound
from loguru import logger

from word_morph import Morph


# URL = "https://docs.google.com/spreadsheets/d/1ROpqWDORLkllt4-QPYiufGg2CRv1oRMxIK35ZU8JnPg/edit?usp=sharing"
URL = "https://docs.google.com/spreadsheets/d/1kY2oVoqIK_5pc_wn6ZjZtojoQa0xnWNOd-SCHyHtGHU/edit?usp=sharing"

CERTIFICATES = "сертификаты"
PARTICIPANTS = "участники"


@dataclass
class Participant:
    fio: str
    phone: str
    email: str
    instagram: str

    @classmethod
    def from_row(cls, row: list[str]) -> 'Participant':
        # TODO: remove sanitization because google form sanitizes data itself
        row = sanitize_temporary_row_data(row)
        return cls(*row)


def sanitize_temporary_row_data(row_data: list[str]) -> list[str]:
    """Temporary hack for current webinar"""
    if len(row_data) == 2:
        logger.debug(f"no email for {row_data[0]}")
        row_data.append('')
    if len(row_data) == 3:
        logger.debug(f"no instagram account for {row_data[0]}")
        row_data.append('')
    if len(row_data) != 4:
        logger.error(f"Invalid row with values: {row_data=}")
    # sanitize name
    row_data[0] = row_data[0].strip()
    # sanitize phone
    phones = row_data[1].strip().split(',')
    if len(phones) > 1:
        logger.warning("{row_data[0]} has multiple phones: {phones}")
    row_data[1] = phones[0].replace(' ', '')
    # sanitize email
    row_data[2] = row_data[2].strip().replace(' ', '')
    # sanitize instagram
    row_data[3] = row_data[3].strip().replace(' ', '')
    return row_data


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


class Webinar:
    def __init__(
            self,
            document: Spreadsheet,
            participants: list[Participant],
            title: str,
            date_str: str,
    ) -> None:
        self.document: Spreadsheet = document
        self.participants: list[Participant] = participants
        self.title: str = title
        self.date_str: str = date_str
        self.certificates_sheet: Worksheet = None

    @classmethod
    def from_url(cls, url: str = URL) -> 'Webinar':
        document = create_spreadsheet(url)
        logger.debug("creating webinar")
        participants_sheet = document.worksheet('участники')
        participants = get_participants_from_sheet(
            participants_sheet,
            first_row=5,  # NOTE: current sheet only, change in future
        )
        webinar_title = get_webinar_topic_from_sheet(participants_sheet)
        webinar_date_str = get_webinar_date_from_sheet(participants_sheet)
        return cls(
            document=document,
            participants=participants,
            title=webinar_title,
            date_str=webinar_date_str,
        )

    def _is_sheet_filled(self, sheet_name: str) -> bool:
        values = self.document.worksheet(sheet_name).get_all_values()
        return len(values) == len(self.participants)

    def certificates_create_sheet(self) -> None:
        # TODO: headers are subject to change
        headers = ['name', 'given_name', 'just_name', 'email', 'custom_text']
        try:
            self.certificates_sheet = self.document.worksheet(CERTIFICATES)
        except WorksheetNotFound:
            logger.info("certificates sheet not found. creating...")
            self.certificates_sheet = self.document.add_worksheet(
                title=CERTIFICATES,
                rows=len(self.participants),
                cols=len(headers),
            )
            logger.info("done")
        if self._is_sheet_filled(CERTIFICATES):
            logger.info("filling certificates")
            for participant in self.participants:
                logger.info("{participant.fio} taken")
                try:
                    morph = Morph.from_fio(participant.fio)
                    logger.info("{participant.fio} morphed")
                except Exception as err:
                    logger.exception("Unable to morph {participant.fio}", err)
                    continue
                row = [
                    participant.fio,
                    morph.fio_given,
                    morph.name,
                    participant.email,
                    '',
                ]
                # append every row because Morph is unstable and may fail
                self.certificates_sheet.append_row(row)
                logger.info("{participant.fio} done")

    def generate_certificates(self) -> None:
        pass

    def send_certificates(self) -> None:
        pass
