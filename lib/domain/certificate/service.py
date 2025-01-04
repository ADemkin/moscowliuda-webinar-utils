from dataclasses import dataclass
from dataclasses import field
from datetime import date

from lib.domain.webinar.enums import WebinarTitle

from .model import Certificate
from .serializer.png_serializer import CertificatePNGSerializer
from .serializer.protocol import Serializable


@dataclass(frozen=True, slots=True)
class CertificateService:
    serializer: Serializable = field(default_factory=CertificatePNGSerializer)

    def generate(
        self,
        title: WebinarTitle,
        started_at: date,
        finished_at: date,
        name: str,
    ) -> Certificate:
        return Certificate(
            title=title,
            name=name,
            started_at=started_at,
            finished_at=finished_at,
            serializer=self.serializer,
        )
