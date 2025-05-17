from dataclasses import dataclass
from dataclasses import field
from datetime import date
from typing import BinaryIO

from lib.const import MONTH2NAME
from lib.domain.webinar.enums import WebinarTitle

from .serializer.png_serializer import CertificatePNGSerializer
from .serializer.protocol import Serializable


@dataclass(frozen=True, slots=True)
class Certificate:
    title: WebinarTitle
    name: str
    started_at: date
    finished_at: date
    serializer: Serializable = field(default_factory=CertificatePNGSerializer)

    def _get_date_text(self) -> str:
        start_day = self.started_at.day
        finish_day = self.finished_at.day
        finish_month = MONTH2NAME[self.finished_at.month]
        year = self.finished_at.year
        if self.finished_at.month == self.started_at.month:
            return f"{start_day} - {finish_day} {finish_month}\n{year} г."
        start_month = MONTH2NAME[self.started_at.month]
        return f"{start_day} {start_month} - {finish_day} {finish_month}\n{year} г."

    def _get_webinar_title_text(self) -> str:
        return {
            WebinarTitle.GRAMMAR: "Формирование базовых\nграмматических представлений",
            WebinarTitle.SPEECH: "Практика запуска речи",
            WebinarTitle.PHRASE: "Приёмы формирования\nфразовой речи",
            WebinarTitle.TEST: "Тестовый вебинар",
        }[self.title]

    def write(self, buffer: BinaryIO) -> None:
        self.serializer.serialize(
            buffer=buffer,
            title=self._get_webinar_title_text(),
            name=self.name,
            date_text=self._get_date_text(),
        )
