from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import replace
from datetime import date
from functools import cached_property
from itertools import count
from pathlib import Path
from time import sleep
from typing import Self

from gspread import Spreadsheet
from gspread import Worksheet

from lib.domain.certificate.service import CertificateService
from lib.domain.contact.service import ContactService
from lib.domain.email.service import EmailService
from lib.domain.webinar.enums import WebinarTitle
from lib.logging import logger
from lib.participants import Participant
from lib.sheets import Sheet

CERTIFICATES_SHEET_NAME = "mailing"


@dataclass(frozen=True)
class Webinar:
    sheet: Sheet
    participants: Iterable[Participant]
    title: WebinarTitle
    started_at: date
    finished_at: date
    certificate_service: CertificateService
    contact_service: ContactService
    email_service: EmailService

    email_sleep: int = 3

    @classmethod
    def from_url(cls, url: str) -> Self:
        logger.debug("creating webinar")
        sheet = Sheet.from_url(url)
        return cls(
            sheet=sheet,
            participants=sheet.get_participants(),
            title=sheet.get_webinar_title(),
            started_at=sheet.get_started_at(),
            finished_at=sheet.get_finished_at(),
            certificate_service=CertificateService(),
            contact_service=ContactService(),
            email_service=EmailService(),
        )

    def with_test_client(self) -> Self:
        return replace(
            self,
            email_service=EmailService.with_test_client(),
            email_sleep=0,
        )

    def prepare_emails(self) -> None:
        logger.info("preparing emails")
        rows = []
        for participant in self.participants:
            message = f"Здравствуйте, {participant.name}! Благодарю вас за участие."
            row = (participant.fio, participant.email, message)
            rows.append(row)
        self.sheet.prepare_emails(rows)
        logger.info("filling certificates done")

    def send_emails_with_certificates(self) -> None:
        logger.info("sending emails")
        for row in self.sheet.get_emails_ready_to_send():
            row_id, full_name, email, message = row
            email_logger = logger.bind(full_name=full_name)
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
            self.sheet.mark_as_sent(row_id)
            email_logger.info("email sent")
            sleep(self.email_sleep)
        logger.info("sending emails done")

    def import_contacts(self) -> Path:
        group = f"{self.title.short()} {self.finished_at.isoformat()}"
        contacts_file = self.contact_service.save_accounts_to_file(
            accounts=list(self.participants),
            group=group,
        )
        logger.info("contacts saved", file=str(contacts_file))
        return contacts_file
