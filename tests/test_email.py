from unittest.mock import MagicMock
from unittest.mock import patch

from lib.send_email import GMail
from lib.send_email import MailStub


def test_mail_creates_from_credentials() -> None:
    user = "username"
    password = "random-password"
    with patch("lib.send_email.SMTP") as smtp_mock:
        GMail.from_credentials(user=user, password=password)
    smtp_mock.assert_called_once_with(user=user, password=password)


def test_mail_sends_email() -> None:
    smtp = MagicMock()
    to = "to@random.com"
    bcc = ["another@random.com", "copy@random.com"]
    subject = "subject"
    contents = "random-content"
    attachments = ["filea", "fileb"]
    GMail(smtp=smtp).send(
        to=to,
        bcc=bcc,
        subject=subject,
        contents=contents,
        attachments=attachments,
    )
    smtp.send.assert_called_once_with(
        to=to,
        bcc=bcc,
        subject=subject,
        contents=contents,
        attachments=attachments,
    )
    MailStub().send(
        to=to,
        bcc=bcc,
        subject=subject,
        contents=contents,
        attachments=attachments,
    )
