import pytest

from lib.clients.db import DB
from lib.domain.inflect.repository import InflectRepository
from lib.domain.inflect.repository import InflectStorage


@pytest.fixture
def db() -> DB:
    return DB.create_in_memory()


@pytest.fixture
def inflect_repo(db: DB) -> InflectRepository:
    inflect_storage = InflectStorage(db=db)
    return InflectRepository(inflect_storage=inflect_storage)


class TestInflectRepoName:
    @staticmethod
    def test_gives_not_confirmed_name_if_name_is_not_found(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected = inflect_repo.get_inflection_by_name("Антон")
        assert not inflected.is_confirmed

    @staticmethod
    def test_gives_not_confirmed_if_name_is_registered(
        inflect_repo: InflectRepository,
    ) -> None:
        inflect_repo.register_unknown_name("Антон")
        inflected = inflect_repo.get_inflection_by_name("Антон")
        assert not inflected.is_confirmed

    @staticmethod
    def test_gives_confirmed_name_if_name_is_set(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected = inflect_repo.set_inflection_by_name("Антон", "Антону")
        assert inflected.is_confirmed
        inflected_got = inflect_repo.get_inflection_by_name("Антон")
        assert inflected == inflected_got

    @staticmethod
    def test_replaces_name_if_name_already_exists(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected_incorrect = inflect_repo.set_inflection_by_name("Антон", "incorrect")
        assert inflected_incorrect.is_confirmed
        inflected_correct = inflect_repo.set_inflection_by_name("Антон", "Антону")
        assert inflected_incorrect != inflected_correct
        assert inflected_correct.is_confirmed
        assert inflected_correct.datv == "Антону"


class TestInflectRepoFamilyName:
    @staticmethod
    def test_gives_not_confirmed_family_name_if_family_name_is_not_found(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected = inflect_repo.get_inflection_by_family_name("Дёмкин")
        assert not inflected.is_confirmed

    @staticmethod
    def test_gives_not_confirmed_if_family_name_is_registered(
        inflect_repo: InflectRepository,
    ) -> None:
        inflect_repo.register_unknown_family_name("Дёмкин")
        inflected = inflect_repo.get_inflection_by_family_name("Дёмкин")
        assert not inflected.is_confirmed

    @staticmethod
    def test_gives_confirmed_family_name_if_family_name_is_set(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected = inflect_repo.set_inflection_by_family_name("Дёмкин", "Дёмкину")
        assert inflected.is_confirmed
        inflected_got = inflect_repo.get_inflection_by_family_name("Дёмкин")
        assert inflected == inflected_got

    @staticmethod
    def test_replaces_family_name_if_family_name_already_exists(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected_incorrect = inflect_repo.set_inflection_by_family_name("Дёмкин", "incorrect")
        assert inflected_incorrect.is_confirmed
        inflected_correct = inflect_repo.set_inflection_by_family_name("Дёмкин", "Дёмкину")
        assert inflected_incorrect != inflected_correct
        assert inflected_correct.is_confirmed
        assert inflected_correct.datv == "Дёмкину"


class TestInflectRepoFatherName:
    @staticmethod
    def test_gives_not_confirmed_father_name_if_father_name_is_not_found(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected = inflect_repo.get_inflection_by_father_name("Андреевна")
        assert not inflected.is_confirmed

    @staticmethod
    def test_gives_not_confirmed_if_father_name_is_registered(
        inflect_repo: InflectRepository,
    ) -> None:
        inflect_repo.register_unknown_father_name("Андреевна")
        inflected = inflect_repo.get_inflection_by_father_name("Андреевна")
        assert not inflected.is_confirmed

    @staticmethod
    def test_gives_confirmed_father_name_if_father_name_is_set(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected = inflect_repo.set_inflection_by_father_name("Андреевна", "Андреевне")
        assert inflected.is_confirmed
        inflected_got = inflect_repo.get_inflection_by_father_name("Андреевна")
        assert inflected == inflected_got

    @staticmethod
    def test_replaces_father_name_if_father_name_already_exists(
        inflect_repo: InflectRepository,
    ) -> None:
        inflected_incorrect = inflect_repo.set_inflection_by_father_name("Андреевна", "incorrect")
        assert inflected_incorrect.is_confirmed
        inflected_correct = inflect_repo.set_inflection_by_father_name("Андреевна", "Андреевне")
        assert inflected_incorrect != inflected_correct
        assert inflected_correct.is_confirmed
        assert inflected_correct.datv == "Андреевне"
