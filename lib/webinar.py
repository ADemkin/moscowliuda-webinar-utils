from datetime import datetime
from functools import cached_property
from os import makedirs
from os import rename
from pathlib import Path
from time import sleep
from typing import Callable

from dotenv import load_dotenv
from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from loguru import logger

from lib.contacts import create_vcard
from lib.contacts import save_vcards_to_file
from lib.factory import WebinarTitles
from lib.factory import get_cert_gen_from_webinar_title
from lib.images import BaseCertificateGenerator
from lib.participants import Participant
from lib.send_email import AbstractMail
from lib.send_email import GMail
from lib.send_email import MailStub
from lib.sheets import get_participants_from_sheet
from lib.sheets import get_webinar_date_and_title
from lib.sheets import open_spreadsheet
from lib.word_morph import offline_morph

URL = "https://docs.google.com/spreadsheets/d/1ilwLmFAQ-FUiRkjVPsLHa4RS9NAxX8chm11siZLYyQU/edit?resourcekey#gid=992781999"  # noqa
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
        test_email: MailStub,
        cert_gen: BaseCertificateGenerator,
        tmp_dir: Path,
        morphological: Callable[[str], str],
    ) -> None:
        self.document: Spreadsheet = document
        self.participants: list[Participant] = participants
        self.title: str = title  # TODO: make enum
        self.date_str: str = date_str
        self.year: int = year
        self.email = email
        self.test_email = test_email
        self.cert_gen = cert_gen
        self.tmp_dir = tmp_dir
        self.morphological = morphological

    @classmethod
    def from_url(cls, url: str = URL) -> "Webinar":
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
        tmp_dir_path = Path("/tmp/webinar/")
        tmp_dir_path.mkdir(exist_ok=True)
        return cls(
            document=document,
            participants=participants,
            title=title,
            date_str=date_str,
            year=year,
            email=GMail.from_environ(),
            test_email=MailStub(),
            cert_gen=cert_gen,
            tmp_dir=tmp_dir_path,
            morphological=offline_morph,
        )

    def _is_sheet_filled(self, sheet_name: str) -> bool:
        values = self.document.worksheet(sheet_name).get_all_values()
        return len(values) == len(self.participants)

    @cached_property
    def cert_sheet(self) -> Worksheet:
        headers = ["fio", "given_fio", "name", "email", "custom_text"]
        try:
            return self.document.worksheet(CERTIFICATES)
        except WorksheetNotFound:
            logger.info("creating certificates sheet")
            return self.document.add_worksheet(
                title=CERTIFICATES,
                rows=len(self.participants),
                cols=len(headers),
            )

    def certificates_sheet_fill(self) -> None:
        logger.info("filling certificates")
        for participant in self.participants:
            logger.info(f"{participant.fio} taken")
            fio_given = self.morphological(participant.fio)
            name = participant.name
            message = f"Здравствуйте, {name}! Благодарю вас за участие."
            row = [
                participant.fio,
                fio_given,
                name,
                participant.email,
                message,
            ]
            self.cert_sheet.append_row(row)
            logger.info(f"{participant.fio} done")
            sleep(1)  # Quota limit is 60 rps
        logger.info("filling certificates done")

    def certificates_generate(self) -> None:
        logger.info("generating certs")
        for row in self.cert_sheet.get_all_values():
            given_fio = row[1]
            logger.debug(f"{given_fio} taken")
            cert_file = self.cert_gen.generate_cerificate(given_fio)
            logger.debug(f"{given_fio} cert path: {str(cert_file)}")
        logger.info("generating certs done")

    def send_emails_with_certificates(self, test: bool = True) -> None:
        email_sender = self.email if not test else self.test_email
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
            email_sender.send(
                to=email,
                bcc=["antondemkin+python@yandex.ru", "moscowliuda@mail.ru"],
                subject=self.title,
                contents=message,
                attachments=[str(ascii_file_name)],
            )
            logger.info(f"{fio} done")
            sleep(3)
        logger.info("sending emails done")

    def get_group_name(self) -> str:
        short_title = {
            WebinarTitles.SPEECH: "П",
            WebinarTitles.GRAMMAR: "Г",
        }[WebinarTitles(self.title.lower())]
        return f"{short_title}{self.date_str.replace(' ', '')} {self.year}"

    def get_participant_vcards(self, group: str) -> list[str]:
        return [
            create_vcard(
                last_name=f"{p.name} {p.family_name}",
                first_name=group,
                email=p.email,
                phone=p.phone,
                organisation=group,
            )
            for p in self.participants
        ]

    def import_contacts(self) -> None:
        group = self.get_group_name()
        vcards = self.get_participant_vcards(group)
        logger.info(f"imported {len(vcards)} contacts")
        webinar_contacts_file = f"{group}.vcf"
        contacts_file = Path("contacts") / webinar_contacts_file
        save_vcards_to_file(contacts_file, vcards)
        logger.info(f"contacts saved to {contacts_file}")
        logger.info("import this file using icloud.com")


if __name__ == "__main__":
    load_dotenv()
    webinar = Webinar.from_url(URL)
    # webinar.import_contacts()
    webinar.certificates_sheet_fill()
    # make sure that names transformed correctly
    # webinar.certificates_generate()
    # make sure that certificates are correct
    # webinar.send_emails_with_certificates(test=False)
