from functools import partial

from pymorphy2 import MorphAnalyzer  # type: ignore
from pyphrasy.inflect import PhraseInflector  # type: ignore
from requests import request
from requests import Response


MORPHER_URL = 'https://ws3.morpher.ru/russian/declension'


class WordMorphError(Exception):
    @classmethod
    def from_resp(cls, response: Response) -> 'WordMorphError':
        status = response.status_code
        message = response.json()['message']
        return cls(f"Status {status!r}: {message!r}")


def get_morph_data(fio: str) -> dict[str, str]:
    """Get response from morpher.ru

    raises WordMorphError

    Documentation:
    * https://morpher.ru/ws3/#declension
    * https://morpher.ru/ws3/#fio-split
    """
    resp = request('get', MORPHER_URL, params={'s': fio, 'format': 'json'})
    if not resp.ok:
        raise WordMorphError.from_resp(resp)
    return resp.json()


def online_morph(fio: str) -> str:
    return get_morph_data(fio)["Д"]


def offline_morph(fio: str) -> str:
    inflect = partial(PhraseInflector(MorphAnalyzer()).inflect, form="datv")
    return ' '.join([inflect(part) for part in fio.split()]).title()
