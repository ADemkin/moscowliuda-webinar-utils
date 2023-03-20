import re
from dataclasses import dataclass
from typing import Sequence

from loguru import logger

from protocols import RowT


@dataclass(frozen=True)
class Participant:
    timestamp: str
    family_name: str
    name: str
    father_name: str
    phone: str
    email: str
    instagram: str = ''

    @classmethod
    def from_row(cls, row: RowT) -> "Participant":
        row_strip: Sequence[str] = [str(i).strip() for i in row]
        return cls(
            timestamp=row_strip[0],
            family_name=row_strip[1],
            name=row_strip[2],
            father_name=row_strip[3],
            phone=normalize_phone_number(row_strip[4]),
            instagram=normalize_instagram_account(row_strip[5]),
            email=normalize_email(row_strip[6]),
        )

    @classmethod
    def from_row_v2(cls, row: RowT) -> "Participant":
        row_strip: Sequence[str] = [str(i).strip() for i in row]
        return cls(
            timestamp=row_strip[0],
            email=normalize_email(row_strip[1]),
            family_name=row_strip[2],
            name=row_strip[3],
            father_name=row_strip[4],
            phone=normalize_phone_number(row_strip[5]),
        )

    @property
    def fio(self) -> str:
        return " ".join((self.family_name, self.name, self.father_name))


def normalize_instagram_account(account: str) -> str:
    return account.lstrip("@")


def normalize_phone_number(number: str) -> str:
    number = number.lstrip("+")
    number = "".join(c for c in number if c.isdigit())
    if number.startswith("8"):
        number = f"7{number[1:]}"
    number = f"+{number}" if number else ''
    return number


def normalize_email(email: str) -> str:
    email = email.lower()
    if not re.match(r"[a-zA-Z0-9._-]+@\w+\.\w+", email):
        logger.warning(f"{email!r} is not a valid email")
    return email
