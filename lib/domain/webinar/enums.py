from __future__ import annotations

from enum import StrEnum
from enum import unique


@unique
class WebinarTitle(StrEnum):
    GRAMMAR = "формирование базовых грамматических представлений"
    SPEECH = "практика запуска речи"
    PHRASE = "приёмы формирования фразовой речи"
    TEST = "test webinar"

    @classmethod
    def from_text(cls, text: str) -> WebinarTitle:
        return cls(text.lower())

    def short(self) -> str:
        return {
            WebinarTitle.GRAMMAR: "грамматика",
            WebinarTitle.SPEECH: "запуск",
            WebinarTitle.TEST: "тест",
            WebinarTitle.PHRASE: "фраза",
        }[self]

    def long(self) -> str:
        return {
            WebinarTitle.GRAMMAR: "Формирование базовых\nграмматических представлений",
            WebinarTitle.SPEECH: "Практика запуска речи",
            WebinarTitle.PHRASE: "Приёмы формирования\nфразовой речи",
            WebinarTitle.TEST: "Тестовый вебинар",
        }[self]
