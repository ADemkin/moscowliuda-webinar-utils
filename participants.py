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
    instagram: str
    email: str

    @classmethod
    def from_row(cls, row: RowT) -> "Participant":
        stripped_row: Sequence[str] = [str(i).strip() for i in row]
        return cls(
            timestamp=stripped_row[0],
            family_name=stripped_row[1],
            name=stripped_row[2],
            father_name=stripped_row[3],
            phone=normalize_phone_number(stripped_row[4]),
            instagram=normalize_instagram_account(stripped_row[5]),
            email=normalize_email(stripped_row[6]),
        )

    @property
    def fio(self) -> str:
        return " ".join((self.family_name, self.name, self.father_name))


def normalize_instagram_account(account: str) -> str:
    return account.lstrip("@")


def normalize_phone_number(number: str) -> str:
    number = number.lstrip("+")
    if number.startswith("8"):
        number = f"7{number[1:]}"
    return "".join(c for c in number if c.isdigit())


def normalize_email(email: str) -> str:
    email = email.lower()
    if not re.match(r"[a-zA-Z0-9._-]+@\w+\.\w+", email):
        logger.warning(f"{email!r} is not a valid email")
    return email
