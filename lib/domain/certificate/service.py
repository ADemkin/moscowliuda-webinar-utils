from dataclasses import dataclass
from dataclasses import field
from datetime import date

from lib.domain.webinar.enums import WebinarTitle

from .model import Certificate
from .serializer.png_serializer import CertificatePNGSerializer
from .serializer.protocol import Serializable


@dataclass(frozen=True, slots=True)
class CertificateService:
    title: WebinarTitle
    started_at: date
    finished_at: date
    serializer: Serializable = field(default_factory=CertificatePNGSerializer)

    def generate(self, name: str) -> Certificate:
        return Certificate(
            title=self.title,
            name=name,
            started_at=self.started_at,
            finished_at=self.finished_at,
            serializer=self.serializer,
        )
