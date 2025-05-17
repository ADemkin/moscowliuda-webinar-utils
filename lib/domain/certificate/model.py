from dataclasses import dataclass
from dataclasses import field
from datetime import date
from typing import BinaryIO

from lib.domain.webinar.enums import WebinarTitle
from lib.utils import date_range_to_text

from .serializer import CertificatePNGSerializer
from .serializer import Serializable


@dataclass(frozen=True, slots=True)
class Certificate:
    title: WebinarTitle
    name: str
    started_at: date
    finished_at: date
    serializer: Serializable = field(default_factory=CertificatePNGSerializer)

    def write(self, buffer: BinaryIO) -> None:
        self.serializer.serialize(
            buffer=buffer,
            title=self.title.long(),
            name=self.name,
            date_text=date_range_to_text(
                started_at=self.started_at,
                finished_at=self.finished_at,
            ),
        )
