from os import urandom
from datetime import datetime
from pathlib import Path

import pytest

from lib.domain.webinar.models import Account
from lib.domain.webinar.models import AccountId
from lib.domain.contacts.repository import VCardRepository
from lib.domain.contacts.service import ContactService


def randstr() -> str:
    return urandom(4).hex()


def randint() -> int:
    return int.from_bytes(urandom(4), 'big')


@pytest.fixture
def contact_service(tmp_path: Path) -> ContactService:
    return ContactService(vcard_repo=VCardRepository(path=tmp_path))


def make_account() -> Account:
    return Account(
        id=AccountId(randint()),
        timestamp=datetime.now(),
        family_name=randstr(),
        name=randstr(),
        father_name=randstr(),
        phone=randstr(),
        email=randstr(),
        webinar_id=randint(),
    )


def test_contact_service(contact_service: ContactService) -> None:
    size = 5
    accounts = [make_account() for _ in range(size)]
    group = randstr()
    path = contact_service.save_accounts_to_file(accounts, group)
    assert path.exists()
    vcards = path.read_text()
    for account in accounts:
        assert account.family_name in vcards
        assert account.name in vcards
        assert account.phone in vcards
        assert account.email in vcards
        assert group in vcards
