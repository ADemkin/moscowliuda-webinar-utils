from models import Participant
from participants import normalize_instagram_account
from participants import normalize_phone_number
from tests.common import create_row

# 'timestamp',
# 'family',
# 'name',
# 'father',
# 'phone',
# 'instagram',
# 'email',
# 'fio_given',
# 'message',


def test_participant_fields_gives_data_from_sheet(create_sheet: any) -> None:
    sheet = create_sheet([
        create_row(
            timestamp="now",
            family="Мазаев",
            name="Антон",
            father="Андреевич",
            email="a@ya.ru",
        ),
    ]).sheet1
    participant = Participant(sheet, 2)
    assert participant.timestamp == "now"
    assert participant.name == "Антон"
    assert participant.family == "Мазаев"
    assert participant.father == "Андреевич"
    assert participant.email == "a@ya.ru"


def test_participant_gives_normalized_fields(create_sheet: any) -> None:
    phone = "89161234567"
    instagram = "@_anton_"
    sheet = create_sheet([
        create_row(
            family="Мазаев",
            name="Антон",
            father="Андреевич",
            phone=phone,
            instagram=instagram,
        ),
    ]).sheet1
    participant = Participant(sheet, 2)
    assert participant.phone == normalize_phone_number(phone)
    assert participant.instagram == normalize_instagram_account(instagram)


def test_participant_gives_correct_given_fio(create_sheet: any) -> None:
    sheet = create_sheet([
        create_row(
            family="Мазаев",
            name="Антон",
            father="Андреевич",
        ),
    ]).sheet1
    participant = Participant(sheet, 2)
    assert participant.fio_given == "Мазаеву Антону Андреевичу"


def test_participant_updates_empty_fields(create_sheet: any) -> None:
    sheet = create_sheet([
        create_row(
            family="Мазаев",
            name="Антон",
            father="Андреевич",
        ),
    ]).sheet1
    participant = Participant(sheet, 2)
    assert participant.message == ''
    message = "Hello, {username}!"
    participant.message = message
    assert participant.message == message
    assert message in sheet.row_values(2)
