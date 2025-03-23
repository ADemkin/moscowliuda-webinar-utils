from __future__ import annotations

from enum import Enum
from enum import unique


@unique
class WebinarTitle(str, Enum):
    GRAMMAR = "формирование базовых грамматических представлений"
    SPEECH = "практика запуска речи"
    PHRASE = "приёмы формирования фразовой речи"
    TEST = "test webinar"

    @classmethod
    def from_text(cls, text: str) -> WebinarTitle:
        return cls(text.lower())

    def short(self) -> str:
        return {
            WebinarTitle.GRAMMAR: "Г",
            WebinarTitle.SPEECH: "П",
            WebinarTitle.TEST: "Т",
            WebinarTitle.PHRASE: "Ф",
        }[self]
