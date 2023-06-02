from functools import partial

from pymorphy2 import MorphAnalyzer  # type: ignore
from pyphrasy.inflect import PhraseInflector  # type: ignore


def offline_morph(fio: str) -> str:
    inflect = partial(PhraseInflector(MorphAnalyzer()).inflect, form="datv")
    return " ".join([inflect(part) for part in fio.split()]).title()
