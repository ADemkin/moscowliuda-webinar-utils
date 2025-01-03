from dataclasses import dataclass
from datetime import date

from lib.domain.webinar.enums import WebinarTitle

from .model import Certificate


@dataclass(frozen=True, slots=True)
class CertificateService:
    title: WebinarTitle
    started_at: date
    finished_at: date

    def generate(self, name: str) -> Certificate:
        return Certificate(
            title=self.title,
            name=name,
            started_at=self.started_at,
            finished_at=self.finished_at,
        )
