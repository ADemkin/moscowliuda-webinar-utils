from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple
from typing import NewType

from lib.domain.webinar.enums import WebinarTitle

WebinarId = NewType("WebinarId", int)
AccountId = NewType("AccountId", int)


class WebinarEntity(NamedTuple):
    id: int
    imported_at: str
    url: str
    title: str
    date_str: str
    year: int


@dataclass(frozen=True, slots=True)
class Webinar:
    id: WebinarId
    imported_at: datetime
    url: str
    title: WebinarTitle
    date_str: str
    year: int

    @classmethod
    def from_row(cls, row: WebinarEntity) -> "Webinar":
        return cls(
            id=WebinarId(row[0]),
            imported_at=datetime.fromisoformat(row[1]),
            url=row[2],
            title=WebinarTitle(row[3]),
            date_str=row[4],
            year=row[5],
        )


class AccountEntity(NamedTuple):
    id: int
    registered_at: str
    family_name: str
    name: str
    father_name: str
    phone: str
    email: str
    webinar_id: int


@dataclass(frozen=True, slots=True)
class Account:
    id: AccountId
    registered_at: datetime
    family_name: str
    name: str
    father_name: str
    phone: str
    email: str
    webinar_id: int

    @classmethod
    def from_row(cls, row: AccountEntity) -> "Account":
        return cls(
            id=AccountId(row[0]),
            registered_at=datetime.fromisoformat(row[1]),
            family_name=row[2],
            name=row[3],
            father_name=row[4],
            phone=row[5],
            email=row[6],
            webinar_id=row[7],
        )
