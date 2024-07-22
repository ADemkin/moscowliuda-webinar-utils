from enum import Enum
from enum import unique


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


@unique
class WebinarTitle(StrEnum):
    GRAMMAR = "формирование базовых грамматических представлений"
    SPEECH = "практика запуска речи"
    PHRASE = "приёмы формирования фразовой речи"
    TEST = "test webinar"
