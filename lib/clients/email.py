from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from io import IOBase
from pathlib import PosixPath
from typing import Any
from typing import Mapping
from typing import Sequence

from yagmail import SMTP

from lib.environment import env_str_field
from lib.logging import logger


class AbstractEmailClient(metaclass=ABCMeta):
    @abstractmethod
    def send(
        self,
        to: str,
        bcc: Sequence[str] | None = None,
        subject: str | None = None,
        contents: str | None = None,
        attachments: Sequence[str | IOBase | PosixPath] | None = None,
    ) -> None:
        ...  # pragma: no cover


@dataclass(slots=True, frozen=True)
class GMailClient(AbstractEmailClient):
    user: str = env_str_field("GMAILACCOUNT")
    password: str = env_str_field("GMAILAPPLICATIONPASSWORD")

    @cached_property
    def smtp(self) -> SMTP:
        return SMTP(user=self.user, password=self.password)

    def send(
        self,
        to: str,
        bcc: Sequence[str] | None = None,
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


@dataclass(frozen=True, slots=True)
class TestEmailClient(AbstractEmailClient):
    _call_args: list[Mapping[str, Any]] = field(default_factory=list)

    def send(
        self,
        to: str,
        bcc: Sequence[str] | None = None,
        subject: str | None = None,
        contents: str | None = None,
        attachments: Sequence[str | IOBase | PosixPath] | None = None,
    ) -> None:
        args = {
            "to": to,
            "bcc": bcc,
            "subject": subject,
            "contents": contents,
            "attachments": attachments,
        }
        self._call_args.append(args)
        logger.debug("TestEmailClient.send: {args}", args=args)

    def is_sent_to(self, to: str) -> bool:
        return to in {call["to"] for call in self._call_args}

    def sent_count(self, to: str) -> int:
        return len([call for call in self._call_args if call["to"] == to])

    def get_attachments(self, to: str) -> list[str]:
        attachments = []
        for call in self._call_args:
            if call["to"] == to:
                attachments.extend(call["attachments"])
        return attachments

    @property
    def total_send_count(self) -> int:
        return len(self._call_args)
