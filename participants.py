from dataclasses import dataclass


@dataclass
class Participant:
    # TODO: check attributes order
    family_name: str
    name: str
    father_name: str
    phone: str
    instagram: str
    email: str

    @classmethod
    def from_row(cls, row: list[str]) -> 'Participant':
        row = normalize_row_data(row)
        return cls(*row)

    @property
    def fio(self) -> str:
        return ' '.join((self.family_name, self.name, self.father_name))


def normalize_instagram_account(account: str) -> str:
    return account.lstrip('@')


def normalize_phone_number(number: str) -> str:
    if number.startswith('8'):
        number = f'7{number[1:]}'
    return ''.join(c for c in number if c.isdigit())


def normalize_row_data(row: list[str]) -> list[str]:
    normalized_row = []
    # skip timestamp from row[0]
    # TODO: check agruments order
    normalized_row.append(row[1])  # family_name
    normalized_row.append(row[2])  # name
    normalized_row.append(row[3])  # father_name
    normalized_row.append(normalize_phone_number(row[4]))  # phone
    normalized_row.append(normalize_instagram_account(row[5]))  # instagram
    normalized_row.append(row[6])  # email
    return normalized_row
