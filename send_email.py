from abc import ABCMeta
from abc import abstractmethod
from io import IOBase
from os import environ
from pathlib import PosixPath
from typing import Union

from yagmail import SMTP


ACCOUNT = "milabaltica@gmail.com"
PASSWORD = environ.get("GMAILAPPLICATIONPASSWORD")


class AbstractMail(metaclass=ABCMeta):
    @abstractmethod
    def send(
            self,
            to: str,
            bcc: list[str] = None,
            subject: str = None,
            contents: str = None,
            attachments: list[Union[str, IOBase, PosixPath]] = None,
    ) -> None:
        ...


class GMail(AbstractMail):
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
    ) -> None:
        self.smtp.send(
            to=to,
            bcc=bcc,
            subject=subject,
            contents=contents,
            attachments=attachments,
        )


class MailStub(AbstractMail):
    def __init__(self) -> None:
        self._call_args: list[dict] = []

    def send(
            self,
            to: str,
            bcc: list[str] = None,
            subject: str = None,
            contents: str = None,
            attachments: list[Union[str, IOBase, PosixPath]] = None,
    ) -> None:
        self._call_args.append(dict(
            to=to,
            bcc=bcc,
            subject=subject,
            contents=contents,
            attachments=attachments,
        ))
        print(f"""--- sending email ---
    {to=}
    {bcc=}
    {subject=}
    {contents=}
    {attachments=}
--- done ---""")

    def assert_email_sent_to(self, to: str) -> bool:
        for call in self._call_args:
            if call['to'] == to:
                return True
        return False


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
    # me = "tonyflexmusic@gmail.com", "jnrbviavjvpxtogz"
    # she = "milabaltyca@gmail.com", "ybullixoirpowibr"
