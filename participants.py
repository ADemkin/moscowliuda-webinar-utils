from dataclasses import dataclass

from protocols import RowT


@dataclass
class Participant:
    timestamp: str
    family_name: str
    name: str
    father_name: str
    phone: str
    instagram: str
    email: str

    @classmethod
    def from_row(cls, row: RowT) -> 'Participant':
        return cls(*normalize_row(row))

    @property
    def fio(self) -> str:
        return ' '.join((self.family_name, self.name, self.father_name))


def normalize_instagram_account(account: str) -> str:
    return account.lstrip('@')


def normalize_phone_number(number: str) -> str:
    number = number.lstrip('+')
    if number.startswith('8'):
        number = f'7{number[1:]}'
    return ''.join(c for c in number if c.isdigit())


def strip(string: str) -> str:
    return string.strip()


def normalize_row(row: RowT) -> list[str]:
    normalized_row = []
    # timetamp
    normalized_row.append(strip(row[0]))  # type: ignore
    # family name
    normalized_row.append(strip(row[1]))  # type: ignore
    # name
    normalized_row.append(strip(row[2]))  # type: ignore
    # father name
    normalized_row.append(strip(row[3]))  # type: ignore
    # phone
    normalized_row.append(normalize_phone_number(row[4]))  # type: ignore
    # instagram
    normalized_row.append(normalize_instagram_account(row[5]))  # type: ignore
    # email
    normalized_row.append(strip(row[6]))  # type: ignore
    return normalized_row
