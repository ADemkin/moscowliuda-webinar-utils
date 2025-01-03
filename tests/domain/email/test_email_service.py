from datetime import date
from pathlib import Path
from random import choice

import pytest

from lib.clients.email import TestEmailClient
from lib.domain.certificate.model import Certificate
from lib.domain.email.service import EmailService
from lib.domain.webinar.enums import WebinarTitle
from lib.environment import EnvironmentVariableNotSetError
from tests.common import randstr


@pytest.fixture
def email_client() -> TestEmailClient:
    return TestEmailClient()


def test_if_environment_not_set_then_raise_exception(email_client: TestEmailClient) -> None:
    with pytest.raises(EnvironmentVariableNotSetError) as err:
        EmailService(email_client=email_client)
    assert "BCC_EMAILS" in str(err.value)


@pytest.mark.parametrize("size", [1, 3, 5])
def test_bcc_emails_are_set_from_environment(
    size: int, monkeypatch: pytest.MonkeyPatch, email_client: TestEmailClient
) -> None:
    bcc_emails = [randstr() for _ in range(size)]
    monkeypatch.setenv("BCC_EMAILS", ",".join(bcc_emails))
    service = EmailService(email_client=email_client)
    assert len(service.bcc_emails) == size
    assert set(service.bcc_emails) == set(bcc_emails)


@pytest.fixture
def email_service(
    email_client: TestEmailClient,
    monkeypatch: pytest.MonkeyPatch,
) -> EmailService:
    bcc_emails = ["test1@test.com", "test2@test.com"]
    monkeypatch.setenv("BCC_EMAILS", ",".join(bcc_emails))
    return EmailService(email_client=email_client)


def test_email_service_send_certificate_email(
    email_service: EmailService,
    email_client: TestEmailClient,
    tmp_path: Path,
) -> None:
    cert_path = tmp_path / "certificate.jpeg"
    cert_path.touch()
    email = "participant@somemail.com"
    message = randstr()
    title = choice(list(WebinarTitle))
    certificate = Certificate(
        title=title,
        name="Мельникова Людмила Андреевна",
        started_at=date(2024, 12, 30),
        finished_at=date(2024, 12, 31),
    )
    email_service.send_certificate_email(
        title=title,
        email=email,
        message=message,
        certificate=certificate,
    )
    assert email_client.total_send_count == 1
    assert email_client.is_sent_to(email)
    assert email_client.sent_count(email) == 1
