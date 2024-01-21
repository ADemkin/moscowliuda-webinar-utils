from datetime import datetime
from os import urandom

import pytest

from lib.clients.db import DB
from lib.domain.inflect.repository import InflectRepository
from lib.domain.inflect.repository import InflectStorage
from lib.domain.inflect.service import InflectService
from lib.domain.webinar.models import Account
from lib.domain.webinar.models import AccountId


def randstr() -> str:
    return urandom(8).hex()


def randint() -> int:
    return int.from_bytes(urandom(4), byteorder="big")


@pytest.fixture
def inflect_repo(db: DB) -> InflectRepository:
    inflect_storage = InflectStorage(db=db)
    return InflectRepository(inflect_storage=inflect_storage)


@pytest.fixture(scope="function")
def inflect_service(db: DB, inflect_repo: InflectRepository) -> InflectService:
    with db.connection() as conn:
        conn.execute("DELETE FROM inflect_name")
        conn.execute("DELETE FROM inflect_family_name")
        conn.execute("DELETE FROM inflect_father_name")
    return InflectService(inflect_repo=inflect_repo)


def make_account(
    *,
    id: int | None = None,
    timestamp: datetime | None = None,
    family_name: str | None = None,
    name: str | None = None,
    father_name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    webinar_id: int | None = None,
) -> Account:
    return Account(
        id=AccountId(id or randint()),
        timestamp=timestamp or datetime.now(),
        family_name=family_name or randstr(),
        name=name or randstr(),
        father_name=father_name or randstr(),
        phone=phone or randstr(),
        email=email or randstr(),
        webinar_id=webinar_id or randint(),
    )


class TestInflectServiceIsConfirmed:
    @staticmethod
    def test_is_fio_confirmed_gives_true_if_all_fio_is_known(
        inflect_repo: InflectRepository,
        inflect_service: InflectService,
    ) -> None:
        inflect_repo.set_inflection_by_name("Иван", "Ивану")
        inflect_repo.set_inflection_by_family_name("Иванов", "Иванову")
        inflect_repo.set_inflection_by_father_name("Иванович", "Ивановичу")
        account = make_account(
            family_name="Иванов",
            name="Иван",
            father_name="Иванович",
        )
        assert inflect_service.is_fio_confirmed(account)

    @staticmethod
    def test_is_fio_confirmed_gives_false_if_all_fio_is_known(
        inflect_repo: InflectRepository,
        inflect_service: InflectService,
    ) -> None:
        inflect_repo.set_inflection_by_name("Иван", "Ивану")
        inflect_repo.set_inflection_by_family_name("Иванов", "Иванову")
        inflect_repo.set_inflection_by_father_name("Иванович", "Ивановичу")
        account = make_account(
            family_name="Иванов",
            name="Иван",
            father_name="Иванович",
        )
        assert inflect_service.is_fio_confirmed(account)

    @staticmethod
    def test_is_fio_confirmed_gives_false_if_name_is_unknown(
        inflect_repo: InflectRepository,
        inflect_service: InflectService,
    ) -> None:
        # inflect_repo.set_inflection_by_name("Иван", "Ивану")
        inflect_repo.set_inflection_by_family_name("Иванов", "Иванову")
        inflect_repo.set_inflection_by_father_name("Иванович", "Ивановичу")
        account = make_account(
            family_name="Иванов",
            name="Иван",
            father_name="Иванович",
        )
        assert not inflect_service.is_fio_confirmed(account)

    @staticmethod
    def test_is_fio_confirmed_gives_false_if_family_name_is_unknown(
        inflect_repo: InflectRepository,
        inflect_service: InflectService,
    ) -> None:
        inflect_repo.set_inflection_by_name("Иван", "Ивану")
        # inflect_repo.set_inflection_by_family_name("Иванов", "Иванову")
        inflect_repo.set_inflection_by_father_name("Иванович", "Ивановичу")
        account = make_account(
            family_name="Иванов",
            name="Иван",
            father_name="Иванович",
        )
        assert not inflect_service.is_fio_confirmed(account)

    @staticmethod
    def test_is_fio_confirmed_gives_false_if_father_name_is_unknown(
        inflect_repo: InflectRepository,
        inflect_service: InflectService,
    ) -> None:
        inflect_repo.set_inflection_by_name("Иван", "Ивану")
        inflect_repo.set_inflection_by_family_name("Иванов", "Иванову")
        # inflect_repo.set_inflection_by_father_name("Иванович", "Ивановичу")
        account = make_account(
            family_name="Иванов",
            name="Иван",
            father_name="Иванович",
        )
        assert not inflect_service.is_fio_confirmed(account)


def test_inflect_service_inflect_account_fio_gives_inflected_fio(
    inflect_repo: InflectRepository,
    inflect_service: InflectService,
) -> None:
    inflect_repo.set_inflection_by_name("Беки", "Беки")
    inflect_repo.set_inflection_by_family_name("Мороз", "Мороз")
    inflect_repo.set_inflection_by_father_name("Иванович", "Ивановичу")
    account = make_account(
        name="Беки",
        family_name="Мороз",
        father_name="Иванович",
    )
    inflected_fio = inflect_service.inflect_account_fio(account)
    assert inflected_fio == "Мороз Беки Ивановичу"


def test_inflect_unknown_account_gives_registered_unknown_part(
    inflect_repo: InflectRepository,
    inflect_service: InflectService,
) -> None:
    account = make_account()
    inflect_service.inflect_account_fio(account)
    assert account.name in inflect_repo.get_unknown_names()
    assert account.family_name in inflect_repo.get_unknown_family_names()
    assert account.father_name in inflect_repo.get_unknown_father_names()
