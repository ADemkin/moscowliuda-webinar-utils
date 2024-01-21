from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from io import IOBase
from pathlib import PosixPath
from typing import Mapping
from typing import Sequence

from loguru import logger
from yagmail import SMTP

from lib.environment import env_str_field


class AbstractMail(metaclass=ABCMeta):
    @abstractmethod
    def send(
        self,
        to: str,
        bcc: Sequence[str] = None,
        subject: str | None = None,
        contents: str | None = None,
        attachments: Sequence[str | IOBase | PosixPath] | None = None,
    ) -> None:
        ...  # pragma: no cover


@dataclass
class GMail(AbstractMail):
    user: str = env_str_field("GMAILACCOUNT")
    password: str = env_str_field("GMAILAPPLICATIONPASSWORD")

    @cached_property
    def smtp(self) -> SMTP:
        return SMTP(user=self.user, password=self.password)

    def send(
        self,
        to: str,
        bcc: Sequence[str] = None,
        subject: str | None = None,
        contents: str | None = None,
        attachments: Sequence[str | IOBase | PosixPath] | None = None,
    ) -> None:
        logger.debug(f"Sending mail to {to}")
        self.smtp.send(
            to=to,
            bcc=bcc,
            subject=subject,
            contents=contents,
            attachments=attachments,
        )
        logger.debug(f"Sending mail to {to} done")


class MailStub(AbstractMail):
    def __init__(self) -> None:
        self._call_args: list[Mapping] = []

    def send(
        self,
        to: str,
        bcc: Sequence[str] = None,
        subject: str | None = None,
        contents: str | None = None,
        attachments: Sequence[str | IOBase | PosixPath] | None = None,
    ) -> None:
        args = dict(
            to=to,
            bcc=bcc,
            subject=subject,
            contents=contents,
            attachments=attachments,
        )
        self._call_args.append(args)
        logger.debug("MailStub.send: {args}", args=args)

    def is_sent_to(self, to: str) -> bool:
        return to in {call["to"] for call in self._call_args}

    def sent_count(self, to: str) -> int:
        return len([call for call in self._call_args if call["to"] == to])

    @property
    def total_send_count(self) -> int:
        return len(self._call_args)
