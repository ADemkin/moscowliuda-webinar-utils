from dataclasses import dataclass
from dataclasses import field

from pymorphy2 import MorphAnalyzer  # type: ignore
from pyphrasy.inflect import PhraseInflector  # type: ignore


@dataclass(slots=True)
class Inflector:
    inflector: PhraseInflector = field(
        default_factory=lambda: PhraseInflector(MorphAnalyzer()),  # type: ignore
    )

    def inflect_datv(self, word: str) -> str:
        return str(self.inflector.inflect(word, form="datv")).title()
