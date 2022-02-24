"""
Трансформировать имя из именительного в дательный падеж.

alternative solution: https://github.com/petrovich/pytrovich
"""

from functools import lru_cache
from typing import Any

from requests import request
from requests import Response


MORPHER_URL = 'https://ws3.morpher.ru/russian/declension'


class WordMorphError(Exception):
    @classmethod
    def from_resp(cls, response: Response) -> 'WordMorphError':
        status = response.status_code
        message = response.json()['message']
        return cls(f"Status {status!r}: {message!r}")


@lru_cache
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


class Morph:
    def __init__(self, data: dict[str, Any], fio: str) -> None:
        self.data: dict[str, Any] = data
        self.fio = fio

    def __repr__(self) -> str:
        return '<NameMorph data={self.data}>'

    @classmethod
    def from_fio(cls, fio: str) -> 'Morph':
        return cls(data=get_morph_data(fio), fio=fio)

    @property
    def fio_given(self) -> str:
        return self.data['Д']

    @property
    def name(self) -> str:
        return self.data['ФИО']['И']
