from dataclasses import dataclass
from datetime import date
from functools import cached_property
from pathlib import Path
from time import sleep
from typing import Iterable

from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound

from lib.domain.contact.service import ContactService
from lib.domain.email.service import EmailService
from lib.domain.inflect.service import InflectService
from lib.domain.webinar.enums import WebinarTitle
from lib.images import BaseCertificateGenerator
from lib.images import cert_gen_factory
from lib.logging import logger
from lib.participants import Participant
from lib.paths import TMP_PATH
from lib.sheets import Sheet

CERTIFICATES = "mailing"
PARTICIPANTS = "Form Responses 1"
DIR_MODE = 0o660


@dataclass(frozen=True)
class Webinar:
    document: Spreadsheet
    participants: Iterable[Participant]
    title: WebinarTitle
    started_at: date
    finished_at: date
    cert_gen: BaseCertificateGenerator
    inflect_service: InflectService
    contact_service: ContactService
    email_service: EmailService

    @classmethod
    def from_url(cls, url: str, test: bool = False) -> "Webinar":
        logger.debug("creating webinar")
        TMP_PATH.mkdir(mode=DIR_MODE, parents=True, exist_ok=True)
        sheet = Sheet.from_url(url)
        title = WebinarTitle.from_text(sheet.get_webinar_title())
        started_at = sheet.get_started_at()
        finished_at = sheet.get_finished_at()
        # get certificates data
        certs_path = TMP_PATH / "certificates" / f"{started_at:%d.%m.%Y}"
        certs_path.mkdir(mode=DIR_MODE, parents=True, exist_ok=True)
        cert_gen = cert_gen_factory(title).create(
            working_dir=certs_path,
            started_at=started_at,
            finished_at=finished_at,
        )
        if test:
            email_sertice = EmailService.with_test_client()
        else:
            email_sertice = EmailService()
        return cls(
            document=sheet.document,
            participants=sheet.participants,
            title=title,
            started_at=started_at,
            finished_at=finished_at,
            cert_gen=cert_gen,
            contact_service=ContactService(),
            inflect_service=InflectService(),
            email_service=email_sertice,
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
                rows=len(list(self.participants)),
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
            WebinarTitle.PHRASE: "Ф",
        }[self.title]
        return f"{short_title}{self.finished_at.isoformat()}"

    def import_contacts(self) -> Path:
        group = self.get_group_name()
        contacts_file = self.contact_service.save_accounts_to_file(
            accounts=list(self.participants),
            group=group,
        )
        logger.info(f"contacts saved to {contacts_file}")
        logger.info("import this file using icloud.com")
        return contacts_file
