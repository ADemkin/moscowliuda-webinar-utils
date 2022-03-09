from loguru import logger

from participants import normalize_instagram_account
from participants import normalize_phone_number
from protocols import ProtoSheet
from word_morph import get_morph_data
from word_morph import WordMorphError


class Participant:
    FIELDS = [
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
    FIELD2INDEX = {idx: i for i, idx in enumerate(FIELDS)}

    def __init__(self, sheet: ProtoSheet, row: int) -> None:
        self._sheet = sheet
        self._row = row
        self._cache: dict[str, str | None] = {}

    def _get_value_by_name(self, name: str) -> str | None:
        if not self._cache:
            self._cache.update(zip(
                self.FIELDS,
                self._sheet.row_values(self._row),
            ))
        if (value := self._cache.get(name)):
            return value
        cell = self._sheet.cell(self._row, self.FIELD2INDEX[name] + 1)
        value = self._cache[name] = cell.value or ''  # type: ignore
        return value

    def _update_value_by_name(self, name: str, value: str) -> None:
        self._sheet.update_cell(self._row, self.FIELD2INDEX[name] + 1, value)
        self._cache[name] = value

    @property
    def timestamp(self) -> str | None:
        return self._get_value_by_name("timestamp")

    @property
    def family(self) -> str | None:
        return self._get_value_by_name("family")

    @property
    def name(self) -> str | None:
        return self._get_value_by_name("name")

    @property
    def father(self) -> str | None:
        return self._get_value_by_name("father")

    @property
    def phone(self) -> str | None:
        phone = self._get_value_by_name("phone")
        if not phone:
            return None
        normalized_phone = normalize_phone_number(phone)
        if phone != normalized_phone:
            self._update_value_by_name("phone", normalized_phone)
        return normalized_phone

    @property
    def instagram(self) -> str | None:
        instagram = self._get_value_by_name("instagram")
        if not instagram:
            return None
        normalized_instagram = normalize_instagram_account(instagram)
        if instagram != normalized_instagram:
            self._update_value_by_name("instagram", normalized_instagram)
        return normalized_instagram

    @property
    def email(self) -> str | None:
        return self._get_value_by_name("email")

    @property
    def fio(self) -> str | None:
        father = self.father
        return f"{self.family} {self.name}" + f" {father}" if father else ""

    @property
    def fio_given(self) -> str | None:
        if (fio := self._get_value_by_name("fio_given")):
            return fio
        if (fio := self.fio):
            fio = get_morph_data(self.fio)["Д"]
            self._update_value_by_name("fio_given", fio)
            return fio
        return None

    @property
    def message(self) -> str | None:
        return self._get_value_by_name("message")

    @message.setter
    def message(self, value: str) -> None:
        self._update_value_by_name("message", value)
