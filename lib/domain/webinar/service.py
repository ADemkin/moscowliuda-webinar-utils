from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Mapping
from typing import Sequence

from loguru import logger

from lib.domain.inflect.service import InflectService
from lib.domain.webinar.enums import WebinarTitle
from lib.domain.webinar.errors import AccountAlreadyExistsError
from lib.domain.webinar.errors import WebinarAlreadyExistsError
from lib.domain.webinar.errors import WebinarNotFoundError
from lib.domain.webinar.models import Account
from lib.domain.webinar.models import Webinar
from lib.domain.webinar.models import WebinarId
from lib.domain.webinar.repository import WebinarRepo
from lib.sheets import Sheet


@dataclass(frozen=True, slots=True)
class WebinarService:
    webinar_repo: WebinarRepo = field(default_factory=WebinarRepo)
    inflect_service: InflectService = field(default_factory=InflectService)

    def get_webinar_by_id(self, webinar_id: WebinarId) -> Webinar | None:
        try:
            return self.webinar_repo.get_webinar_by_id(webinar_id)
        except WebinarNotFoundError:
            logger.error(f"Webinar {webinar_id} not found")
            return None

    def get_accounts_by_webinar_id(self, webinar_id: WebinarId) -> Sequence[Account]:
        return self.webinar_repo.get_accounts_by_webinar_id(webinar_id)

    def import_webinar_and_accounts_by_url(
        self,
        url: str,
    ) -> tuple[Webinar, Sequence[Account]]:
        logger.debug(f"Importing webinar and accounts by url: {url}")
        sheet = Sheet.from_url(url)
        try:
            title = WebinarTitle(sheet.title)
        except ValueError:
            logger.error(f"Unknown webinar title: {sheet.title}")
            raise
        webinar: Webinar
        try:
            webinar = self.webinar_repo.add_webinar(
                url=url,
                date_str=sheet.date_str,
                title=title,
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
                    registered_at=participant.timestamp or datetime.now(),
                    family_name=participant.family_name,
                    name=participant.name,
                    father_name=participant.father_name,
                    phone=participant.phone,
                    email=participant.email,
                )
                logger.info(f"Account {account} added")
                if not self.inflect_service.is_fio_confirmed(account):
                    self.inflect_service.register_uninflected_parts(account)
                    logger.info("Uninflected parts registered")
                accounts.append(account)
            except AccountAlreadyExistsError:
                logger.info(f"Account {participant} already exists")
        logger.debug(f"Imported {len(accounts)} accounts for webinar {webinar}")
        return webinar, accounts

    def import_webinars_and_accounts_by_urls(
        self,
        urls: Sequence[str],
    ) -> Mapping[Webinar, Sequence[Account]]:
        webinar2accounts: dict[Webinar, Sequence[Account]] = defaultdict(list)
        for url in urls:
            webinar, accounts = self.import_webinar_and_accounts_by_url(url)
            webinar2accounts[webinar] = accounts
        return webinar2accounts

    def get_webinars(self) -> Sequence[Webinar]:
        return self.webinar_repo.get_webinars()
