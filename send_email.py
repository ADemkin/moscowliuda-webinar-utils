from io import IOBase
from os import environ
from pathlib import PosixPath
from typing import Union

from yagmail import SMTP


ACCOUNT = "milabaltica@gmail.com"
PASSWORD = environ.get("GMAILAPPLICATIONPASSWORD")


class GMail:
    def __init__(self, smtp: SMTP) -> None:
        self.smtp = smtp

    @classmethod
    def from_credentials(cls, user: str, password: str) -> 'GMail':
        return cls(smtp=SMTP(user=user, password=password))

    @classmethod
    def from_environ(cls) -> 'GMail':
        return cls(smtp=SMTP(
            user=environ.get("GMAILACCOUNT"),
            password=environ.get("GMAILAPPLICATIONPASSWORD"),
        ))

    def send(
            self,
            to: str,
            bcc: list[str] = None,
            subject: str = None,
            contents: str = None,
            attachments: list[Union[str, IOBase, PosixPath]] = None,
    ) -> dict:
        return self.smtp.send(
            to=to,
            bcc=bcc,
            subject=subject,
            contents=contents,
            attachments=attachments,
        )


class MailStub:
    def send(
            self,
            to: str,
            bcc: list[str] = None,
            subject: str = None,
            contents: str = None,
            attachments: list[Union[str, IOBase, PosixPath]] = None,
    ) -> None:
        print(f"""--- sending email ---
    {to=}
    {bcc=}
    {subject=}
    {contents=}
    {attachments=}
--- done ---""")


def run_tests():
    from unittest.mock import patch
    # test_mail_creates_from_credentials
    user = 'username'
    password = 'random-password'
    with patch(f"{__name__}.SMTP") as smtp_mock:
        mail = GMail.from_credentials(user=user, password=password)
    smtp_mock.assert_called_once_with(user=user, password=password)

    from unittest.mock import MagicMock
    # test_mail_sends_email
    smtp = MagicMock()
    to = 'to@random.com'
    bcc = ['another@random.com', 'copy@random.com']
    subject = 'subject'
    contents = 'random-content'
    attachments = ['filea', 'fileb']
    mail = GMail(smtp=smtp)
    mail.send(
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
    mail = MailStub()
    mail.send(
        to=to,
        bcc=bcc,
        subject=subject,
        contents=contents,
        attachments=attachments,
    )


if __name__ == '__main__':
    run_tests()
