from gspread import Spreadsheet
from loguru import logger

from participants import normalize_instagram_account
from participants import normalize_phone_number
from word_morph import get_morph_data
from word_morph import WordMorphError


CELLS = [
    'timestamp',
    'family',
    'name',
    'father',
    'phone',
    'instagram',
    'email',
    'fio_given',
    'message',
]


class Participant:
    def __init__(self, sheet: Spreadsheet, row: int) -> None:
        self._sheet = sheet
        self._row = row
        self._cache = {}

    def _get_value_by_name(self, name: str) -> str:
        if not self._cache:
            self._cache.update(zip(CELLS, self._sheet.row_values(self._row)))
        if (value := self._cache.get(name)):
            return value
        value = self._sheet.cell(self._row, CELLS.index(name) + 1).value or ''
        self._cache[name] = value
        return value

    def _update_value_by_name(self, name: str, value: str) -> None:
        self._sheet.update_cell(self._row, CELLS.index(name) + 1, value)
        self._cache[name] = value

    @property
    def timestamp(self) -> str:
        return self._get_value_by_name("timestamp")

    @property
    def family(self) -> str:
        return self._get_value_by_name("family")

    @property
    def name(self) -> str:
        return self._get_value_by_name("name")

    @property
    def father(self) -> str:
        return self._get_value_by_name("father")

    @property
    def phone(self) -> str:
        phone = self._get_value_by_name("phone")
        normalized_phone = normalize_phone_number(phone)
        if phone != normalized_phone:
            self._update_value_by_name("phone", normalized_phone)
        return normalized_phone

    @property
    def instagram(self) -> str:
        instagram = self._get_value_by_name("instagram")
        normalized_instagram = normalize_instagram_account(instagram)
        if instagram != normalized_instagram:
            self._update_value_by_name("instagram", normalized_instagram)
        return normalized_instagram

    @property
    def email(self) -> str:
        return self._get_value_by_name("email")

    @property
    def fio(self) -> str:
        father = self.father
        return f"{self.family} {self.name}" + f" {father}" if father else ""

    @property
    def fio_given(self) -> str:
        fio = self._get_value_by_name("fio_given")
        if not fio:
            try:
                fio = get_morph_data(self.fio)["Д"]
            except WordMorphError as err:
                logger.exception(err)
            self._update_value_by_name("fio_given", fio)
        return fio

    @property
    def message(self) -> str:
        return self._get_value_by_name("message")

    @message.setter
    def message(self, value: str) -> None:
        self._update_value_by_name("message", value)
