from os import environ
from os import urandom
from unittest.mock import patch

import pytest

from lib.clients.email import GMail
from lib.clients.email import MailStub


def randstr() -> str:
    return urandom(8).hex()


@pytest.fixture
def smtp_mock():
    with patch("lib.clients.email.SMTP") as smtp_mock:
        yield smtp_mock


def test_gmail_can_be_created_from_env() -> None:
    user = randstr()
    password = randstr()
    environ["GMAILACCOUNT"] = user
    environ["GMAILAPPLICATIONPASSWORD"] = password
    gmail = GMail()
    assert gmail.user == user
    assert gmail.password == password


def test_gmail_creates_smtp_with_correct_credentials(smtp_mock):
    user = randstr()
    password = randstr()
    GMail(user=user, password=password).send(to="")
    smtp_mock.assert_called_once_with(user=user, password=password)


def test_gmail_uses_same_connection_for_all_sends(smtp_mock):
    gmail = GMail(user="", password="")
    gmail.send(to="")
    gmail.send(to="")
    assert smtp_mock.return_value.send.call_count == 2


def test_gmail_calls_smtp_send_with_correct_arguments(smtp_mock):
    to = randstr()
    bcc = [randstr(), randstr()]
    subject = randstr()
    contents = randstr()
    attachments = [randstr(), randstr()]
    GMail(user="", password="").send(
        to=to,
        bcc=bcc,
        subject=subject,
        contents=contents,
        attachments=attachments,
    )
    smtp_mock.return_value.send.assert_called_once_with(
        to=to,
        bcc=bcc,
        subject=subject,
        contents=contents,
        attachments=attachments,
    )


@pytest.mark.parametrize("size", [1, 2, 3])
def test_mailstub_keeps_all_calls(size: int):
    emails = {randstr() for _ in range(size)}
    assert len(emails) == size
    mail_stub = MailStub()
    for email in emails:
        mail_stub.send(to=email)
    assert mail_stub.total_send_count == size
    for email in emails:
        assert mail_stub.is_sent_to(to=email)
        assert mail_stub.sent_count(to=email) == 1
