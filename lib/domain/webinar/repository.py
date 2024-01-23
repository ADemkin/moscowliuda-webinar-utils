import sqlite3
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Sequence

from lib.clients.db import DB
from lib.domain.webinar.enums import WebinarTitle
from lib.domain.webinar.errors import AccountAlreadyExistsError
from lib.domain.webinar.errors import AccountNotFoundError
from lib.domain.webinar.errors import WebinarAlreadyExistsError
from lib.domain.webinar.errors import WebinarNotFoundError
from lib.domain.webinar.models import Account
from lib.domain.webinar.models import AccountEntity
from lib.domain.webinar.models import AccountId
from lib.domain.webinar.models import Webinar
from lib.domain.webinar.models import WebinarEntity
from lib.domain.webinar.models import WebinarId


@dataclass(frozen=True, slots=True)
class WebinarRepo:
    db: DB = field(default_factory=DB)

    def add_webinar(self, url: str, date_str: str, title: WebinarTitle, year: int) -> Webinar:
        query = f"""
            INSERT INTO webinar (
                url,
                date_str,
                title,
                year
            )
            VALUES (
                :url,
                :date_str,
                :title,
                :year
            )
            RETURNING
                {', '.join(WebinarEntity._fields)}
        """
        params = {
            "url": url,
            "date_str": date_str,
            "title": title,
            "year": year,
        }
        try:
            with self.db.connection() as connection:
                row = connection.execute(query, params).fetchone()
            return Webinar.from_row(row)
        except sqlite3.IntegrityError as err:
            message = f"Webinar with {url=!r} already exists"
            raise WebinarAlreadyExistsError(message) from err

    def get_webinar_by_id(self, webinar_id: int) -> Webinar:
        query = f"""
            SELECT {', '.join(WebinarEntity._fields)}
            FROM webinar
            WHERE id = :id
        """
        params = {"id": webinar_id}
        with self.db.connection() as connection:
            if row := connection.execute(query, params).fetchone():
                return Webinar.from_row(row)
        raise WebinarNotFoundError(f"Webinar with {webinar_id=!r} not found")

    def get_webinar_by_url(self, url: str) -> Webinar:
        query = """
            SELECT id, imported_at, url, title, date_str, year
            FROM webinar
            WHERE url = :url
        """
        params = {"url": url}
        with self.db.connection() as connection:
            if row := connection.execute(query, params).fetchone():
                return Webinar.from_row(row)
        raise WebinarNotFoundError(f"Webinar with {url=!r} not found")

    def add_account(
        self,
        webinar_id: int,
        registered_at: datetime,
        family_name: str,
        name: str,
        father_name: str,
        phone: str,
        email: str,
    ) -> Account:
        query = f"""
            INSERT INTO account (
                webinar_id,
                registered_at,
                family_name,
                name,
                father_name,
                phone,
                email
            )
            VALUES (
                :webinar_id,
                :registered_at,
                :family_name,
                :name,
                :father_name,
                :phone,
                :email
            )
            RETURNING
                {', '.join(AccountEntity._fields)}
        """
        params = {
            "registered_at": registered_at,
            "webinar_id": webinar_id,
            "family_name": family_name,
            "name": name,
            "father_name": father_name,
            "phone": phone,
            "email": email,
        }
        try:
            with self.db.connection() as connection:
                row = connection.execute(query, params).fetchone()
            return Account.from_row(row)
        except sqlite3.IntegrityError as err:
            message = f"Account with {email=!r} or {phone=!r} already exists"
            raise AccountAlreadyExistsError(message) from err

    def get_account_by_id(self, account_id: AccountId) -> Account:
        query = f"""
            SELECT
                {', '.join(AccountEntity._fields)}
            FROM account
            WHERE id = :id
        """
        params = {"id": account_id}
        with self.db.connection() as connection:
            if row := connection.execute(query, params).fetchone():
                return Account.from_row(row)
        raise AccountNotFoundError(f"Account with id={account_id!r} not found")

    def get_webinars(self) -> Sequence[Webinar]:
        query = f"""
            SELECT {', '.join(WebinarEntity._fields)}
            FROM webinar
        """
        with self.db.connection() as connection:
            rows = connection.execute(query).fetchall()
        return [Webinar.from_row(row) for row in rows]

    def get_accounts_by_webinar_id(self, webinar_id: WebinarId) -> Sequence[Account]:
        query = f"""
            SELECT
                {', '.join(AccountEntity._fields)}
            FROM account
            WHERE webinar_id = :webinar_id
        """
        params = {"webinar_id": webinar_id}
        with self.db.connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Account.from_row(row) for row in rows]
