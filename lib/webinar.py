from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from functools import cached_property
from pathlib import Path
from time import sleep
from typing import Self

from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound

from lib.domain.certificate.service import CertificateService
from lib.domain.contact.service import ContactService
from lib.domain.email.service import EmailService
from lib.domain.webinar.enums import WebinarTitle
from lib.logging import logger
from lib.participants import Participant
from lib.sheets import Sheet

CERTIFICATES = "mailing"


@dataclass(frozen=True)
class Webinar:
    document: Spreadsheet
    participants: Iterable[Participant]
    title: WebinarTitle
    started_at: date
    finished_at: date
    certificate_service: CertificateService
    contact_service: ContactService
    email_service: EmailService

    _email_sleep: int = 3
    _sheet_sleep: int = 1

    @classmethod
    def from_url(cls, url: str) -> Self:
        logger.debug("creating webinar")
        sheet = Sheet.from_url(url)
        email_service = EmailService()
        return cls(
            document=sheet.document,
            participants=sheet.participants,
            title=sheet.get_webinar_title(),
            started_at=sheet.get_started_at(),
            finished_at=sheet.get_finished_at(),
            certificate_service=CertificateService(),
            contact_service=ContactService(),
            email_service=email_service,
        )

    @classmethod
    def from_url_with_test_email_client(cls, url: str) -> Self:
        logger.debug("creating webinar")
        sheet = Sheet.from_url(url)
        email_service = EmailService.with_test_client()
        return cls(
            document=sheet.document,
            participants=sheet.participants,
            title=sheet.get_webinar_title(),
            started_at=sheet.get_started_at(),
            finished_at=sheet.get_finished_at(),
            certificate_service=CertificateService(),
            contact_service=ContactService(),
            email_service=email_service,
        )

    @cached_property
    def cert_sheet(self) -> Worksheet:
        headers = ["fio", "[deprecated]", "is_sent", "email", "custom_text"]
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
            participant_logger = logger.bind(full_name=participant.fio)
            message = f"Здравствуйте, {participant.name}! Благодарю вас за участие."
            row = [participant.fio, "-", "no", participant.email, message]
            self.cert_sheet.append_row(row)
            participant_logger.info("done")
            sleep(self._sheet_sleep)  # Quota limit is 60 rpm
        logger.info("filling certificates done")

    def send_emails_with_certificates(self) -> None:
        logger.info("sending emails")
        for i, row in enumerate(self.cert_sheet.get_all_values()):
            full_name, _, is_email_sent, email, message = row
            email_logger = logger.bind(full_name=full_name)
            if is_email_sent == "yes":
                email_logger.info("email already sent")
                continue
            certificate = self.certificate_service.generate(
                title=self.title,
                started_at=self.started_at,
                finished_at=self.finished_at,
                name=full_name,
            )
            email_logger.debug("sending email")
            self.email_service.send_certificate_email(
                title=self.title,
                email=email,
                message=message,
                certificate=certificate,
            )
            row_number = i + 1
            self.cert_sheet.update_cell(row_number, 3, "yes")
            email_logger.info("email sent")
            sleep(self._email_sleep)
        logger.info("sending emails done")

    def import_contacts(self) -> Path:
        group = f"{self.title.short()} {self.finished_at.isoformat()}"
        contacts_file = self.contact_service.save_accounts_to_file(
            accounts=list(self.participants),
            group=group,
        )
        logger.info(f"contacts saved to {contacts_file}")
        logger.info("import this file using icloud.com")
        return contacts_file
