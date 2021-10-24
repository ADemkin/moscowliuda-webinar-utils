"""
Трансформировать имя из именительного в дательный падеж.

alternative solution: https://github.com/petrovich/pytrovich
"""

from requests import request


MORPHER_URL = 'https://ws3.morpher.ru/russian/declension'


class WordMorphError(Exception):
    pass


def get_fio_in_given_form(fio: str) -> str:
    """Make response to web service and data from answer.

    raises WordMorphError

    Documentation: https://morpher.ru/ws3/#declension
    """
    resp = request('get', MORPHER_URL, params={'s': fio, 'format': 'json'})
    json = resp.json()
    if not resp.ok:
        raise WordMorphError(f'Error ({resp.status_code}): {json["message"]!r}')
    if (given_form := json.get('Д')):
        return given_form
    raise WordMorphError(f'Invalid response: {resp.text!r}')


def run_tests() -> None:
    import pytest  # pylint: disable=import-outside-toplevel
    name_form_and_given_form = [
        ('Пупкин Василий Александрович', 'Пупкину Василию Александровичу'),
        ('Ермолина Лариса Васильевна', 'Ермолиной Ларисе Васильевне'),
    ]
    for name_form, given_form in name_form_and_given_form:
        assert get_fio_in_given_form(name_form) == given_form
    with pytest.raises(WordMorphError) as err:
        get_fio_in_given_form("not in russian")
    assert str(err.value) == "Error (496): 'Не найдено русских слов.'", err.value
    print('tests ok')


if __name__ == '__main__':
    run_tests()
