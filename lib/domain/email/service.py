from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from loguru import logger

from lib.clients.email import AbstractEmailClient
from lib.clients.email import GMailClient
from lib.clients.email import TestEmailClient
from lib.domain.webinar.enums import WebinarTitle
from lib.environment import env_str_tuple_field
from lib.paths import TMP_PATH


@dataclass(frozen=True, slots=True)
class EmailService:
    email_client: AbstractEmailClient = field(default_factory=GMailClient)
    bcc_emails: tuple[str, ...] = env_str_tuple_field("BCC_EMAILS")
    tmp_path: Path = field(default=TMP_PATH)

    @classmethod
    def with_test_client(cls) -> "EmailService":
        return cls(email_client=TestEmailClient())

    def _save_certificate_to_ascii_file(self, cert_path: Path) -> Path:
        self.tmp_path.mkdir(mode=0o660, parents=True, exist_ok=True)
        ascii_file_name = self.tmp_path / "certificate.jpeg"
        cert_path.rename(ascii_file_name)
        return ascii_file_name

    def send_certificate_email(
        self,
        title: WebinarTitle,
        email: str,
        message: str,
        cert_path: Path,
    ) -> None:
        logger.debug(f"Sending certificate message to {email}...")
        self.email_client.send(
            to=email,
            bcc=self.bcc_emails,
            subject=title.title(),
            contents=message,
            attachments=[str(self._save_certificate_to_ascii_file(cert_path))],
        )
        logger.debug(f"Certificate message sent to {email}.")
