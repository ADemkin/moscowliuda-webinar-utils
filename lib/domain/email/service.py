from dataclasses import dataclass
from dataclasses import field
from io import BytesIO

from lib.clients.email import AbstractEmailClient
from lib.clients.email import GMailClient
from lib.clients.email import TestEmailClient
from lib.domain.certificate.model import Certificate
from lib.domain.webinar.enums import WebinarTitle
from lib.environment import env_str_tuple_field
from lib.logging import logger


@dataclass(frozen=True, slots=True)
class EmailService:
    email_client: AbstractEmailClient = field(default_factory=GMailClient)
    bcc_emails: tuple[str, ...] = env_str_tuple_field("BCC_EMAILS")

    @classmethod
    def with_test_client(cls) -> "EmailService":
        return cls(email_client=TestEmailClient())

    def send_certificate_email(
        self,
        title: WebinarTitle,
        email: str,
        message: str,
        certificate: Certificate,
    ) -> None:
        logger.debug(f"Sending certificate message to {email}...")
        buffer = BytesIO()
        certificate.write(buffer)
        buffer.seek(0)
        self.email_client.send(
            to=email,
            bcc=self.bcc_emails,
            subject=title.title(),
            contents=message,
            attachments=[buffer],
        )
        logger.debug(f"Certificate message sent to {email}.")
