from xml.etree.ElementTree import fromstring

from requests import request


MORPHER_URL = 'https://ws3.morpher.ru/russian/declension'


def get_name_in_given_form(name: str) -> str:
    resp = request('get', MORPHER_URL, params={'s': name})
    resp.raise_for_status()
    given_form = fromstring(resp.text).find("Д")
    if given_form is None:
        raise ValueError(f"Given form not found in response: {resp.text}")
    return given_form.text
