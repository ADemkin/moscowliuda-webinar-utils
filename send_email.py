from abc import ABCMeta, abstractmethod
from io import IOBase
from os import environ
from pathlib import PosixPath
from typing import Sequence, Union

from yagmail import SMTP


class AbstractMail(metaclass=ABCMeta):
    @abstractmethod
    def send(
        self,
        to: str,
        bcc: list[str] = None,
        subject: str = None,
        contents: str = None,
        attachments: Sequence[Union[str, IOBase, PosixPath]] = None,
    ) -> None:
        ...


class GMail(AbstractMail):
    def __init__(self, smtp: SMTP) -> None:
        self.smtp = smtp

    @classmethod
    def from_credentials(cls, user: str, password: str) -> "GMail":
        return cls(smtp=SMTP(user=user, password=password))

    @classmethod
    def from_environ(cls) -> "GMail":
        try:
            return cls(
                smtp=SMTP(
                    user=environ["GMAILACCOUNT"],
                    password=environ["GMAILAPPLICATIONPASSWORD"],
                )
            )
        except KeyError as err:
            raise RuntimeError(
                "Environment variables not test: "
                "GMAILACCOUNT, GMAILAPPLICATIONPASSWORD"
            ) from err

    def send(
        self,
        to: str,
        bcc: list[str] = None,
        subject: str = None,
        contents: str = None,
        attachments: Sequence[Union[str, IOBase, PosixPath]] = None,
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
        attachments: Sequence[Union[str, IOBase, PosixPath]] = None,
    ) -> None:
        self._call_args.append(
            dict(
                to=to,
                bcc=bcc,
                subject=subject,
                contents=contents,
                attachments=attachments,
            )
        )
        print(
            f"""--- sending email ---
    {to=}
    {bcc=}
    {subject=}
    {contents=}
    {attachments=}
--- done ---"""
        )

    def assert_email_sent_to(self, to: str) -> bool:
        for call in self._call_args:
            if call["to"] == to:
                return True
        return False
