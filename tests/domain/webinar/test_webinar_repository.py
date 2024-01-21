import os

import pytest

from lib.clients.db import DB
from lib.domain.webinar.errors import AccountAlreadyExistsError
from lib.domain.webinar.errors import AccountNotFoundError
from lib.domain.webinar.errors import WebinarAlreadyExistsError
from lib.domain.webinar.errors import WebinarNotFoundError
from lib.domain.webinar.models import AccountId
from lib.domain.webinar.models import Webinar
from lib.domain.webinar.models import WebinarId
from lib.domain.webinar.repository import WebinarRepo


@pytest.fixture(scope="session")
def db() -> DB:
    return DB.create_in_memory()


@pytest.fixture
def webinar_repo(db: DB) -> WebinarRepo:
    return WebinarRepo(db=db)


def add_random_webinar(webinar_repo: WebinarRepo) -> Webinar:
    webinar_url = f"https://webinar-url.some/{os.urandom(8).hex()}/#"
    title = "random webinar title"
    date_str = "2020-01-01"
    year = 2020
    return webinar_repo.add_webinar(url=webinar_url, date_str=date_str, title=title, year=year)


def test_webinar_repo_add_webinar_gives_webinar_model(
    webinar_repo: WebinarRepo,
) -> None:
    webinar_url = "https://webinar-url.some/0/#"
    title = "random webinar title"
    date_str = "2020-01-01"
    year = 2020
    webinar = webinar_repo.add_webinar(url=webinar_url, date_str=date_str, title=title, year=year)
    assert webinar.url == webinar_url
    assert webinar.title == title
    assert webinar.date_str == date_str
    assert webinar.year == year
    webinar_got = webinar_repo.get_webinar_by_id(webinar_id=webinar.id)
    assert webinar_got == webinar


def test_webinar_repo_gives_existing_webinar_by_url(
    webinar_repo: WebinarRepo,
) -> None:
    webinar = add_random_webinar(webinar_repo=webinar_repo)
    webinar_got = webinar_repo.get_webinar_by_url(url=webinar.url)
    assert webinar_got == webinar


def test_webinar_repo_raises_error_when_webinar_id_not_found(
    webinar_repo: WebinarRepo,
) -> None:
    with pytest.raises(WebinarNotFoundError):
        webinar_repo.get_webinar_by_id(webinar_id=WebinarId(9999))


def test_webinar_repo_raises_error_when_webinar_url_not_found(
    webinar_repo: WebinarRepo,
) -> None:
    with pytest.raises(WebinarNotFoundError):
        webinar_repo.get_webinar_by_url(url="someurl")


def test_webinar_repo_raises_error_when_webinar_already_exists(
    webinar_repo: WebinarRepo,
) -> None:
    webinar_url = "https://webinar-url.some/2/#"
    title = "random webinar title"
    date_str = "2020-01-01"
    year = 2020
    webinar_repo.add_webinar(url=webinar_url, date_str=date_str, title=title, year=year)
    with pytest.raises(WebinarAlreadyExistsError):
        webinar_repo.add_webinar(url=webinar_url, date_str=date_str, title=title, year=year)


def test_webinar_repo_add_account_gives_account_model(
    webinar_repo: WebinarRepo,
) -> None:
    webinar = add_random_webinar(webinar_repo=webinar_repo)
    account = webinar_repo.add_account(
        webinar_id=webinar.id,
        family_name="Петров",
        name="Пётр",
        father_name="Петрович",
        phone="+7 (916) 123-45-67",
        email="someemail",
    )
    assert account.webinar_id == webinar.id
    assert account.family_name == "Петров"
    assert account.name == "Пётр"
    assert account.father_name == "Петрович"
    assert account.phone == "+7 (916) 123-45-67"
    assert account.email == "someemail"
    account_got = webinar_repo.get_account_by_id(account_id=account.id)
    assert account_got == account


def test_webinar_repo_raises_error_when_account_not_found(
    webinar_repo: WebinarRepo,
) -> None:
    with pytest.raises(AccountNotFoundError):
        webinar_repo.get_account_by_id(account_id=AccountId(9999))


def test_webinar_repo_raises_error_when_account_email_already_exists(
    webinar_repo: WebinarRepo,
) -> None:
    webinar = add_random_webinar(webinar_repo=webinar_repo)
    email = "someemail@somedomain.com"
    webinar_repo.add_account(
        webinar_id=webinar.id,
        family_name="Петров",
        name="Пётр",
        father_name="Петрович",
        phone="+7 (916) 321-54-76",
        email=email,
    )
    with pytest.raises(AccountAlreadyExistsError):
        webinar_repo.add_account(
            webinar_id=webinar.id,
            family_name="Петров",
            name="Пётр",
            father_name="Петрович",
            phone="+7 (916) 123-45-67",
            email=email,
        )


def test_webinar_repo_raises_error_when_account_phone_already_exists(
    webinar_repo: WebinarRepo,
) -> None:
    webinar = add_random_webinar(webinar_repo=webinar_repo)
    phone = "+7 (916) 321-54-76"
    webinar_repo.add_account(
        webinar_id=webinar.id,
        family_name="Петров",
        name="Пётр",
        father_name="Петрович",
        phone=phone,
        email="someemail",
    )
    with pytest.raises(AccountAlreadyExistsError):
        webinar_repo.add_account(
            webinar_id=webinar.id,
            family_name="Петров",
            name="Пётр",
            father_name="Петрович",
            phone=phone,
            email="someotheremail",
        )


def test_webinar_repo_gives_all_webinars(webinar_repo: WebinarRepo) -> None:
    webinars_before = webinar_repo.get_all_webinars()
    webinar1 = add_random_webinar(webinar_repo=webinar_repo)
    webinar2 = add_random_webinar(webinar_repo=webinar_repo)
    assert webinar1 not in webinars_before
    assert webinar2 not in webinars_before
    webinars = webinar_repo.get_all_webinars()
    assert len(webinars) == len(webinars_before) + 2
    assert webinar1 in webinars
    assert webinar2 in webinars


def test_webinar_repo_gives_all_webinar_accounts_by_webinar_id(
    webinar_repo: WebinarRepo,
) -> None:
    webinar = add_random_webinar(webinar_repo=webinar_repo)
    assert webinar_repo.get_all_accounts_by_webinar_id(webinar_id=webinar.id) == []
    account1 = webinar_repo.add_account(
        webinar_id=webinar.id,
        family_name="Петров",
        name="Пётр",
        father_name="Петрович",
        phone="+7 (916) 123-45-67",
        email="someemail",
    )
    account2 = webinar_repo.add_account(
        webinar_id=webinar.id,
        family_name="Петров",
        name="Пётр",
        father_name="Петрович",
        phone="+7 (916) 321-54-76",
        email="someotheremail",
    )
    accounts = webinar_repo.get_all_accounts_by_webinar_id(webinar_id=webinar.id)
    assert len(accounts) == 2
    assert account1 in accounts
    assert account2 in accounts
