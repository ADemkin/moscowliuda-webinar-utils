from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Sequence

from lib.domain.contact.models import VCard
from lib.domain.contact.repository import VCardRepository
from lib.logging import logger
from lib.participants import Participant


@dataclass(frozen=True, slots=True)
class ContactService:
    vcard_repo: VCardRepository = field(default_factory=VCardRepository)

    @staticmethod
    def create_vcard(account: Participant, group: str) -> VCard:
        return VCard(
            last_name=f"{account.name} {account.family_name}",
            first_name=group,
            email=account.email,
            phone=account.phone,
            organisation=group,
        )

    def save_accounts_to_file(
        self,
        accounts: Sequence[Participant],
        group: str,
    ) -> Path:
        logger.debug(f"Saving {len(accounts)} accounts to file")
        vcards = [self.create_vcard(account, group) for account in accounts]
        path = self.vcard_repo.save_vcards_to_file(vcards, group)
        logger.debug(f"Saved accounts to {path}")
        return path
