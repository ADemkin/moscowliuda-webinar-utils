import sqlite3
from dataclasses import dataclass
from dataclasses import field
from lib.clients.db import DB
from lib.domain.webinar.models import Account
from lib.domain.webinar.models import Webinar
from lib.domain.webinar.errors import AccountAlreadyExistsError
from lib.domain.webinar.errors import WebinarAlreadyExistsError
from lib.domain.webinar.errors import AccountNotFoundError
from lib.domain.webinar.errors import WebinarNotFoundError


@dataclass(frozen=True, slots=True)
class WebinarRepo:
    db: DB = field(default_factory=DB)

    def add_webinar(self, url: str, date_str: str, title: str, year: int) -> Webinar:
        query = """
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
                id,
                imported_at,
                url,
                title,
                date_str,
                year
        """
        params = {"url": url, "date_str": date_str, "title": title, "year": year}
        try:
            row = self.db.connection.execute(query, params).fetchone()
        except sqlite3.IntegrityError as err:
            message = f"Webinar with {url=!r} already exists"
            raise WebinarAlreadyExistsError(message) from err
        return Webinar.from_row(row)

    def get_webinar_by_id(self, webinar_id: int) -> Webinar:
        query = """
            SELECT id, imported_at, url, title, date_str, year
            FROM webinar
            WHERE id = :id
        """
        params = {"id": webinar_id}
        if row := self.db.connection.execute(query, params).fetchone():
            return Webinar.from_row(row)
        raise WebinarNotFoundError(f"Webinar with {webinar_id=!r} not found")

    def get_webinar_by_url(self, url: str) -> Webinar:
        query = """
            SELECT id, imported_at, url, title, date_str, year
            FROM webinar
            WHERE url = :url
        """
        params = {"url": url}
        if row := self.db.connection.execute(query, params).fetchone():
            return Webinar.from_row(row)
        raise WebinarNotFoundError(f"Webinar with {url=!r} not found")

    def add_account(
            self,
            webinar_id: int,
            family_name: str,
            name: str,
            father_name: str,
            phone: str,
            email: str,
    ) -> Account:
        query = """
            INSERT INTO account (
                webinar_id,
                family_name,
                name,
                father_name,
                phone,
                email
            )
            VALUES (
                :webinar_id,
                :family_name,
                :name,
                :father_name,
                :phone,
                :email
            )
            RETURNING
                id,
                timestamp,
                family_name,
                name,
                father_name,
                phone,
                email,
                webinar_id
        """
        params = {
            "webinar_id": webinar_id,
            "family_name": family_name,
            "name": name,
            "father_name": father_name,
            "phone": phone,
            "email": email,
        }
        try:
            resp = self.db.connection.execute(query, params)
        except sqlite3.IntegrityError as err:
            message = f"Account with {email=!r} or {phone=!r} already exists"
            raise AccountAlreadyExistsError(message) from err
        row = resp.fetchone()
        return Account.from_row(row)

    def get_account_by_id(self, account_id: int) -> Account:
        query = """
            SELECT
                id,
                timestamp,
                family_name,
                name,
                father_name,
                phone,
                email,
                webinar_id
            FROM account
            WHERE id = :id
        """
        params = {"id": account_id}
        resp = self.db.connection.execute(query, params)
        if row := resp.fetchone():
            return Account.from_row(row)
        raise AccountNotFoundError(f"Account with id={account_id!r} not found")
