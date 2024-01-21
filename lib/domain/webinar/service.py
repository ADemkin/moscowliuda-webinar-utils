from dataclasses import dataclass
from dataclasses import field
from typing import Sequence

from loguru import logger

from lib.domain.webinar.errors import AccountAlreadyExistsError
from lib.domain.webinar.errors import WebinarAlreadyExistsError
from lib.domain.webinar.models import Account
from lib.domain.webinar.models import Webinar
from lib.domain.webinar.repository import WebinarRepo
from lib.sheets import Sheet


@dataclass(slots=True)
class WebinarService:
    webinar_repo: WebinarRepo = field(default_factory=WebinarRepo)

    def import_webinar_and_accounts_by_url(self, url: str) -> Sequence[Account]:
        logger.debug(f"Importing webinar and accounts by url: {url}")
        sheet = Sheet.from_url(url)
        webinar: Webinar
        try:
            webinar = self.webinar_repo.add_webinar(
                url=url,
                date_str=sheet.date_str,
                title=sheet.title,
                year=sheet.year,
            )
            logger.info(f"Webinar {webinar} added")
        except WebinarAlreadyExistsError:
            logger.info(f"Webinar {url} already exists")
            webinar = self.webinar_repo.get_webinar_by_url(url)
        accounts: list[Account] = []
        for participant in sheet.participants:
            try:
                account = self.webinar_repo.add_account(
                    webinar_id=webinar.id,
                    family_name=participant.family_name,
                    name=participant.name,
                    father_name=participant.father_name,
                    phone=participant.phone,
                    email=participant.email,
                )
                logger.info(f"Account {account} added")
                accounts.append(account)
            except AccountAlreadyExistsError:
                logger.info(f"Account {participant} already exists")
        logger.debug(f"Imported {len(accounts)} accounts for webinar {webinar}")
        return accounts

    def import_webinars_and_accounts_by_urls(self, urls: Sequence[str]) -> Sequence[Account]:
        accounts: list[Account] = []
        for url in urls:
            accounts.extend(self.import_webinar_and_accounts_by_url(url))
        return accounts
