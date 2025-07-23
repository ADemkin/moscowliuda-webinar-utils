from datetime import date
from random import choice
from typing import Generator
from unittest.mock import MagicMock

import pytest

from lib.clients.email import EmailTestClient
from lib.domain.certificate.model import Certificate
from lib.domain.email.service import EmailService
from lib.domain.webinar.enums import WebinarTitle
from lib.environment import EnvironmentVariableNotSetError
from tests.common import randstr
from tests.common import ru_faker


@pytest.fixture
def email_client() -> EmailTestClient:
    return EmailTestClient()


@pytest.fixture
def bcc_emails(monkeypatch: pytest.MonkeyPatch) -> tuple[str, ...]:
    bcc_emails = [randstr() for _ in range(3)]
    monkeypatch.setenv("BCC_EMAILS", ",".join(bcc_emails))
    return tuple(bcc_emails)


def test_if_environment_not_set_then_raise_exception(email_client: EmailTestClient) -> None:
    with pytest.raises(EnvironmentVariableNotSetError) as err:
        EmailService(email_client=email_client)
    assert "BCC_EMAILS" in str(err.value)


def test_bcc_emails_are_set_from_environment(
    email_client: EmailTestClient,
    bcc_emails: list[str],
) -> None:
    service = EmailService(email_client=email_client)
    assert service.bcc_emails == bcc_emails


@pytest.fixture(autouse=True)
def sleep_mock(monkeypatch: pytest.MonkeyPatch) -> Generator[MagicMock]:
    with monkeypatch.context() as m:
        sleep_mock = MagicMock()
        m.setattr("lib.domain.email.service.sleep", sleep_mock)
        yield sleep_mock


def test_email_service_send_certificate_email(
    sleep_mock: MagicMock,
    email_client: EmailTestClient,
) -> None:
    email = "participant@somemail.com"
    title: WebinarTitle = choice(list(WebinarTitle))  # type: ignore[assignment]
    certificate = Certificate(
        title=title,
        name=ru_faker.name(),
        started_at=date(2024, 12, 30),
        finished_at=date(2024, 12, 31),
    )
    email_service = EmailService(
        email_client=email_client,
        bcc_emails=("does-not-matter",),
    )
    email_service.send_certificate_email(
        title=title,
        email=email,
        message=randstr(),
        certificate=certificate,
    )
    assert email_client.total_send_count == 1
    assert email_client.is_sent_to(email)
    assert email_client.sent_count(email) == 1
    sleep_mock.assert_called_once_with(email_service.send_timeout_sec)
