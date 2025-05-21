from dataclasses import dataclass
from typing import Self
from dataclasses import field
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.clients.email import AbstractEmailClient
from lib.clients.email import GMailClient
from lib.clients.email import TestEmailClient
from lib.domain.certificate.model import Certificate
from lib.domain.webinar.enums import WebinarTitle
from lib.environment import env_str_tuple_field


@dataclass(frozen=True, slots=True)
class EmailService:
    email_client: AbstractEmailClient = field(default_factory=GMailClient)
    bcc_emails: tuple[str, ...] = env_str_tuple_field("BCC_EMAILS")

    @classmethod
    def with_test_client(cls) -> Self:
        return cls(email_client=TestEmailClient())

    def send_certificate_email(
        self,
        title: WebinarTitle,
        email: str,
        message: str,
        certificate: Certificate,
    ) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "certificate.png"
            with path.open("wb") as fd:
                certificate.write(fd)
            self.email_client.send(
                to=email,
                bcc=self.bcc_emails,
                subject=title.title(),
                contents=message,
                attachments=[path],
            )

    def send_email(
        self,
        title: str,
        email: str,
        message: str,
    ) -> None:
        self.email_client.send(
            to=email,
            bcc=self.bcc_emails,
            subject=title,
            contents=message,
        )
