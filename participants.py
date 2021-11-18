from dataclasses import dataclass


@dataclass
class Participant:
    fio: str
    phone: str
    email: str
    instagram: str

    @classmethod
    def from_row(cls, row: list[str]) -> 'Participant':
        row = sanitize_temporary_row_data(row)
        return cls(*row)


def sanitize_temporary_row_data(row_data: list[str]) -> list[str]:
    """Temporary hack for current webinar"""
    if len(row_data) == 2:
        logger.debug(f"no email for {row_data[0]}")
        row_data.append('')
    if len(row_data) == 3:
        logger.debug(f"no instagram account for {row_data[0]}")
        row_data.append('')
    if len(row_data) != 4:
        logger.error(f"Invalid row with values: {row_data=}")
    # sanitize name
    row_data[0] = row_data[0].strip()
    # sanitize phone
    phones = row_data[1].strip().split(',')
    if len(phones) > 1:
        logger.warning(f"{row_data[0]} has multiple phones: {phones}")
    row_data[1] = phones[0].replace(' ', '')
    # sanitize email
    row_data[2] = row_data[2].strip().replace(' ', '')
    # sanitize instagram
    row_data[3] = row_data[3].strip().replace(' ', '')
    return row_data
