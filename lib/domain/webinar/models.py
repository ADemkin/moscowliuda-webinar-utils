from dataclasses import dataclass
from datetime import datetime
from typing import NewType

WebinarId = NewType("WebinarId", int)
AccountId = NewType("AccountId", int)


@dataclass(frozen=True, slots=True)
class Webinar:
    id: WebinarId
    imported_at: datetime
    url: str
    title: str
    date_str: str
    year: int

    @classmethod
    def from_row(cls, row: tuple) -> "Webinar":
        return cls(
            id=row[0],
            imported_at=row[1],
            url=row[2],
            title=row[3],
            date_str=row[4],
            year=row[5],
        )


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
    def from_row(cls, row: tuple) -> "Account":
        return cls(
            id=row[0],
            registered_at=datetime.fromisoformat(row[1]),
            family_name=row[2],
            name=row[3],
            father_name=row[4],
            phone=row[5],
            email=row[6],
            webinar_id=row[7],
        )
