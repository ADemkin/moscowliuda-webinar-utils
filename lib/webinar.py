from functools import cached_property
from pathlib import Path
from time import sleep

from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from loguru import logger

from lib.domain.contact.service import ContactService
from lib.domain.email.service import EmailService
from lib.domain.inflect.service import InflectService
from lib.domain.webinar.enums import WebinarTitle
from lib.factory import get_cert_gen_from_webinar_title
from lib.images import BaseCertificateGenerator
from lib.participants import Participant
from lib.paths import TMP_PATH
from lib.sheets import Sheet

CERTIFICATES = "mailing"
PARTICIPANTS = "Form Responses 1"


class Webinar:
    def __init__(
        self,
        document: Spreadsheet,
        participants: list[Participant],
        title: WebinarTitle,
        date_str: str,
        year: int,
        cert_gen: BaseCertificateGenerator,
        tmp_dir: Path,
        inflect_service: InflectService,
        contact_service: ContactService,
        email_service: EmailService,
    ) -> None:
        self.document: Spreadsheet = document
        self.participants: list[Participant] = participants
        self.title: WebinarTitle = title
        self.date_str: str = date_str
        self.year: int = year
        self.cert_gen = cert_gen
        self.tmp_dir = tmp_dir
        self.contact_service = contact_service
        self.inflect_service = inflect_service
        self.email_service = email_service

    @classmethod
    def from_url(cls, url: str, test: bool = False) -> "Webinar":
        logger.debug("creating webinar")
        sheet = Sheet.from_url(url)
        year = sheet.year
        # get certificates data
        certs_path = TMP_PATH / "certificates" / f"{sheet.date_str} {year}"
        certs_path.mkdir(mode=0o660, parents=True, exist_ok=True)
        cert_gen = get_cert_gen_from_webinar_title(sheet.title).create(
            working_dir=certs_path,
            date=sheet.date_str,
            year=year,
        )
        tmp_dir_path = TMP_PATH
        tmp_dir_path.mkdir(mode=0o660, parents=True, exist_ok=True)
        if test:
            email_sertive = EmailService.with_test_client()
        else:
            email_sertive = EmailService()
        return cls(
            document=sheet.document,
            participants=sheet.participants,
            title=WebinarTitle(sheet.title.lower()),
            date_str=sheet.date_str,
            year=year,
            cert_gen=cert_gen,
            tmp_dir=tmp_dir_path,
            contact_service=ContactService(),
            inflect_service=InflectService(),
            email_service=email_sertive,
        )

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
            fio_given = self.inflect_service.inflect_account_fio(participant)
            message = f"Здравствуйте, {participant.name}! Благодарю вас за участие."
            row = [
                participant.fio,
                fio_given,
                "no",
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
            cert_file = self.cert_gen.generate_certificate(given_fio)
            logger.debug(f"{given_fio} cert path: {str(cert_file)}")
        logger.info("generating certs done")

    def send_emails_with_certificates(self) -> None:
        logger.info("sending emails")
        for i, row in enumerate(self.cert_sheet.get_all_values()):
            fio, given_fio, is_email_sent, email, message = row
            logger.debug(f"{fio} taken")
            if is_email_sent == "yes":
                logger.debug(f"{fio} do not need to send email")
                continue
            cert_file = self.cert_gen.generate_certificate(given_fio)
            logger.info(f"{fio} sending email to {email}")
            self.email_service.send_certificate_email(
                title=self.title,
                email=email,
                message=message,
                cert_path=cert_file,
            )
            row_number = i + 1
            self.cert_sheet.update_cell(row_number, 3, "yes")
            logger.info(f"{fio} done")
            sleep(3)
        logger.info("sending emails done")

    def get_group_name(self) -> str:
        short_title = {
            WebinarTitle.SPEECH: "П",
            WebinarTitle.GRAMMAR: "Г",
            WebinarTitle.TEST: "Т",
        }[self.title]
        return f"{short_title}{self.date_str.replace(' ', '')} {self.year}"

    def import_contacts(self) -> Path:
        group = self.get_group_name()
        contacts_file = self.contact_service.save_accounts_to_file(
            accounts=self.participants,
            group=group,
        )
        logger.info(f"contacts saved to {contacts_file}")
        logger.info("import this file using icloud.com")
        return contacts_file
