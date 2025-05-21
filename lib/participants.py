from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Self

from lib.protocols import RowT
from lib.utils import get_datetime_from_sheet_timestamp
from lib.utils import normalize_email
from lib.utils import normalize_phone_number

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(slots=True, frozen=True)
class Participant:
    timestamp: datetime | None
    family_name: str
    name: str
    father_name: str
    phone: str
    email: str
    instagram: str = ""

    @classmethod
    def from_row_v2(cls, row: RowT) -> Self:
        row_strip: Sequence[str] = [str(i).strip() for i in row]
        return cls(
            timestamp=get_datetime_from_sheet_timestamp(row_strip[0]),
            email=normalize_email(row_strip[1]),
            family_name=row_strip[2],
            name=row_strip[3],
            father_name=row_strip[4],
            phone=normalize_phone_number(row_strip[5]),
        )

    @property
    def fio(self) -> str:
        return f"{self.family_name} {self.name} {self.father_name}"
