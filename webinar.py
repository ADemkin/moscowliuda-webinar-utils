from datetime import datetime
from os import makedirs
from os import rename
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Callable
import atexit

from dotenv import load_dotenv
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from loguru import logger

from factory import get_cert_gen_from_webinar_title
from images import BaseCertificateGenerator
from participants import Participant
from send_email import AbstractMail
from send_email import GMail
from send_email import MailStub
from sheets import get_participants_from_sheet
from sheets import get_webinar_date_and_title
from sheets import open_spreadsheet
from word_morph import offline_morph


URL = "https://docs.google.com/spreadsheets/d/18opjgDC1dQn7An3rJ5IYyfgzErFXQG0mMspPsNkajAk/edit?resourcekey#gid=1484958473"
CERTIFICATES = "mailing"
PARTICIPANTS = "Form Responses 1"


class Webinar:
    def __init__(
            self,
            document: Spreadsheet,
            participants: list[Participant],
            title: str,
            date_str: str,
            year: int,
            email: AbstractMail,
            cert_gen: BaseCertificateGenerator,
            tmp_dir: Path,
            morphological: Callable[[str], str],
    ) -> None:
        self.document: Spreadsheet = document
        self.participants: list[Participant] = participants
        self.title: str = title
        self.date_str: str = date_str
        self.year: int = year
        self._cert_sheet: Worksheet = None
        self.email = email
        self.cert_gen = cert_gen
        self.tmp_dir = tmp_dir
        self.morphological = morphological

    @classmethod
    def from_url(cls, url: str = URL) -> 'Webinar':
        document = open_spreadsheet(url)
        logger.debug("creating webinar")
        # get participants
        participants = get_participants_from_sheet(
            document.worksheet(PARTICIPANTS),
            first_row=1,
        )
        # get title and date
        date_str, title = get_webinar_date_and_title(document.title)
        year = datetime.now().year
        # get certificates data
        certs_dir = Path("certificates") / f"{date_str} {year}"
        makedirs(str(certs_dir), mode=0o700, exist_ok=True)
        cert_gen = get_cert_gen_from_webinar_title(title).create(
            working_dir=certs_dir,
            date=date_str,
            year=year,
        )
        # create mailer
        # email = MailStub()
        email = GMail.from_environ()
        working_dir = TemporaryDirectory()
        atexit.register(working_dir.cleanup)
        return cls(
            document=document,
            participants=participants,
            title=title,
            date_str=date_str,
            year=year,
            email=email,
            cert_gen=cert_gen,
            tmp_dir=Path(working_dir.name),
            morphological=offline_morph,
        )

    def _is_sheet_filled(self, sheet_name: str) -> bool:
        values = self.document.worksheet(sheet_name).get_all_values()
        return len(values) == len(self.participants)

    @property
    def cert_sheet(self) -> Worksheet:
        headers = ['fio', 'given_fio', 'name', 'email', 'custom_text']
        # TODO: add instagram after email

        if self._cert_sheet is None:
            try:
                self._cert_sheet = self.document.worksheet(CERTIFICATES)
            except WorksheetNotFound:
                logger.info("creating certificates sheet")
                self._cert_sheet = self.document.add_worksheet(
                    title=CERTIFICATES,
                    rows=len(self.participants),
                    cols=len(headers),
                )
                logger.info("done")
        return self._cert_sheet

    def certificates_sheet_is_filled(self) -> bool:
        cert_sheet_rows = self.cert_sheet.get_all_values()
        if len(cert_sheet_rows) == len(self.participants):
            logger.debug("already filled")
            return True
        elif len(cert_sheet_rows) > len(self.participants):
            logger.warning("already filled but rows > participants")
            return True
        elif 0 < len(cert_sheet_rows) < len(self.participants):
            logger.error("looks like table is filled up partially")
        return False

    def certificates_sheet_fill(self) -> None:
        logger.info("filling certificates")
        if self.certificates_sheet_is_filled():
            return
        for participant in self.participants:
            logger.info(f"{participant.fio} taken")
            fio_given = self.morphological(participant.fio)
            message = f'Здравствуйте, {participant.name}! Благодарю вас за участие.'
            row = [
                participant.fio,
                fio_given,
                participant.name,
                participant.email,
                message,
            ]
            self.cert_sheet.append_row(row)
            logger.info(f"{participant.fio} done")
            sleep(1)  # Quota limit is 60 rps
        logger.info("filling certificates done")

    def certificates_generate(self) -> None:
        logger.info("generating certs")
        # TODO: get exact values, even if they are ''
        for row in self.cert_sheet.get_all_values():
            given_fio = row[1]
            logger.debug(f"{given_fio} taken")
            cert_file = self.cert_gen.generate_cerificate(given_fio)
            logger.debug(f"{given_fio} cert path: {str(cert_file)}")
        logger.info("generating certs done")

    def send_emails_with_certificates(self) -> None:
        # headers = ['name', 'given_name', 'just_name', 'email', 'custom_text']
        logger.info("sending emails")
        for row in self.cert_sheet.get_all_values():
            fio, given_fio, _, email, message = row
            logger.debug(f"{fio} taken")
            cert_file = self.cert_gen.generate_cerificate(given_fio)
            logger.info(f"{fio} sending email to {email}")
            ascii_file_name = self.tmp_dir / "certificate.jpeg"
            rename(cert_file, ascii_file_name)
            logger.debug(f"cert file: {ascii_file_name}")
            self.email.send(
                to=email,
                bcc=["antondemkin+python@yandex.ru", "moscowliuda@mail.ru"],
                subject=self.title,
                contents=message,
                attachments=[str(ascii_file_name)],
            )
            logger.info(f"{fio} done")
            # TODO: mark email as sent in google sheet
            sleep(3)
        logger.info("sending emails done")


if __name__ == '__main__':
    load_dotenv()
    webinar = Webinar.from_url(URL)
    # webinar.certificates_sheet_fill()
    # make sure that names transformed correctly
    # webinar.certificates_generate()
    # make sure that certificates are correct
    # webinar.send_emails_with_certificates()
