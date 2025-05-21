from os import urandom
from pathlib import Path

import pytest

from lib.domain.contact.repository import VCardRepository
from lib.domain.contact.service import ContactService
from lib.participants import Participant


def randstr() -> str:
    return urandom(4).hex()


def randint() -> int:
    return int.from_bytes(urandom(4), "big")


def make_participant() -> Participant:
    return Participant(
        timestamp=None,
        family_name=randstr(),
        name=randstr(),
        father_name=randstr(),
        phone=randstr(),
        email=randstr(),
    )


@pytest.fixture
def contact_service(tmp_path: Path) -> ContactService:
    return ContactService(vcard_repo=VCardRepository(path=tmp_path))


@pytest.mark.parametrize("size", [1, 5, 10])
def test_contact_service(contact_service: ContactService, size: int) -> None:
    accounts = [make_participant() for _ in range(size)]
    group = randstr()
    path = contact_service.save_accounts_to_file(accounts, group)
    assert path.exists()
    vcards = path.read_text()
    assert "BEGIN:VCARD" in vcards
    assert "END:VCARD" in vcards
    for account in accounts:
        assert account.family_name in vcards
        assert account.name in vcards
        assert account.phone in vcards
        assert account.email in vcards
        assert group in vcards
