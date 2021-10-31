from dataclasses import dataclass
from time import sleep
from datetime import datetime
from pathlib import Path
import sys

from gspread import service_account
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from loguru import logger

from images import Certificate
from send_email import GMail
from word_morph import Morph


URL_BASE = "https://docs.google.com/spreadsheets/d/"
# URL = URL_BASE + "1ROpqWDORLkllt4-QPYiufGg2CRv1oRMxIK35ZU8JnPg"  # real
URL = URL_BASE + "1kY2oVoqIK_5pc_wn6ZjZtojoQa0xnWNOd-SCHyHtGHU"  # copy

CERTIFICATES = "сертификаты"
PARTICIPANTS = "участники"

EMAIL_MESSAGE_TEMPLATE = """Hello, {name}!

Thank you for participating in my webinar!

Your certificate is in attachment.
{custom_text}

Regards, Python
"""


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
            year: int,
            certs_dir: Path,
            cert_template: Path,
            email: GMail,
    ) -> None:
        self.document: Spreadsheet = document
        self.participants: list[Participant] = participants
        self.title: str = title
        self.date_str: str = date_str
        self.year: int = year
        self.cert_sheet: Worksheet = None
        self.certs_dir = certs_dir
        self.cert_template = cert_template
        self.email = email

    @classmethod
    def from_url(cls, url: str = URL) -> 'Webinar':
        document = create_spreadsheet(url)
        logger.debug("creating webinar")
        participants_sheet = document.worksheet('участники')
        participants = get_participants_from_sheet(
            participants_sheet,
            first_row=5,  # NOTE: current sheet only, change in future
        )
        title = get_webinar_topic_from_sheet(participants_sheet)
        date_str = get_webinar_date_from_sheet(participants_sheet)
        year = datetime.now().year
        cert_template = Path("template_without_date.jpeg")
        if not cert_template.exists():
            logger.error(f"{cert_template} not found")
            sys.exit(1)
        email = GMail.from_environ()
        return cls(
            document=document,
            participants=participants,
            title=title,
            date_str=date_str,
            year=year,
            certs_dir=Path('.') / 'certificates' / f"{date_str}-{year}",
            cert_template=cert_template,
            email=email,
        )

    def _is_sheet_filled(self, sheet_name: str) -> bool:
        values = self.document.worksheet(sheet_name).get_all_values()
        return len(values) == len(self.participants)

    def certificates_sheet_create(self, fill: bool = False) -> None:
        # TODO: headers are subject to change
        headers = ['fio', 'given_fio', 'name', 'email', 'custom_text']
        try:
            self.cert_sheet = self.document.worksheet(CERTIFICATES)
        except WorksheetNotFound:
            logger.info("certificates sheet not found. creating...")
            self.cert_sheet = self.document.add_worksheet(
                title=CERTIFICATES,
                rows=len(self.participants),
                cols=len(headers),
            )
            logger.info("done")
        if fill and not self._is_sheet_filled(CERTIFICATES):
            self.certificates_sheet_fill()

    def certificates_sheet_fill(self) -> None:
        logger.info("filling certificates")
        for participant in self.participants:
            # TODO: check if participant already in table
            logger.info("{participant.fio} taken")
            try:
                morph = Morph.from_fio(participant.fio)
                logger.info("{participant.fio} morphed")
                fio_given = morph.fio_given
                name = morph.name
            except Exception as err:
                logger.exception("Unable to morph {participant.fio}", err)
                fio_given = ''
                name = ''
            row = [
                participant.fio,
                fio_given,
                name,
                participant.email,
                '',
            ]
            # append every row because Morph is unstable and may fail
            self.cert_sheet.append_row(row)
            logger.info("{participant.fio} done")

    def certificates_generate(self) -> None:
        logger.info("generating certs")
        for _, given_fio, _, _, _ in self.cert_sheet.get_all_values():
            logger.debug(f"{given_fio} taken")
            cert = Certificate.create(
                template=self.cert_template,
                certs_dir=self.certs_dir,
                name=given_fio,
                date=self.date_str,
                year=self.year,
            )
            cert.create_file()
            logger.debug(f"{given_fio} cert path: {str(cert.path)}")
        logger.info("generating certs done")

    def send_emails_with_certificates(self) -> None:
        # headers = ['name', 'given_name', 'just_name', 'email', 'custom_text']
        logger.info("sending emails")
        rows = self.cert_sheet.get_all_values()
        for fio, given_fio, name, email, custom_text in rows:
            logger.debug(f"{fio} taken")
            cert = Certificate.create(
                template=self.cert_template,
                certs_dir=self.certs_dir,
                name=given_fio,
                date=self.date_str,
                year=self.year,
            )
            if not cert.exists():
                logger.debug(f"{fio} generating cert")
                cert.create_file()
                logger.debug(f"{fio} generating cert done")
            message = EMAIL_MESSAGE_TEMPLATE.format(
                name=name,
                custom_text=custom_text if custom_text else '',
            )
            logger.info(f"{fio} sending email to {email}")
            self.email.send(
                # to=email,  # TODO
                to=f"antondemkin+{fio.replace(' ', '-')}@yandex.ru",
                bcc=["antondemkin+python@yandex.ru"],
                subject=self.title,
                contents=message,
                attachments=[str(cert.path)],
            )
            logger.info(f"{fio} done")
            sleep(3)
        logger.info("sending emails done")


if __name__ == '__main__':
    webinar = Webinar.from_url(URL)
    webinar.certificates_sheet_create(fill=False)
    webinar.certificates_sheet_fill()
    webinar.certificates_generate()
    webinar.send_emails_with_certificates()
