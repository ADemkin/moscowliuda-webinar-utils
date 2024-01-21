from dataclasses import dataclass
from dataclasses import field

from loguru import logger

from lib.domain.inflect.repository import InflectRepository
from lib.domain.webinar.models import Account
from lib.participants import Participant


@dataclass(frozen=True, slots=True)
class InflectService:
    inflect_repo: InflectRepository = field(default_factory=InflectRepository)

    def is_fio_confirmed(self, account: Account | Participant) -> bool:
        if not self.inflect_repo.get_inflection_by_name(
            name=account.name,
        ).is_confirmed:
            return False
        if not self.inflect_repo.get_inflection_by_family_name(
            family_name=account.family_name,
        ).is_confirmed:
            return False
        if not self.inflect_repo.get_inflection_by_father_name(
            father_name=account.father_name,
        ).is_confirmed:
            return False
        return True

    def register_uninflected_parts(self, account: Account | Participant) -> None:
        if not self.inflect_repo.get_inflection_by_name(
            name=account.name,
        ).is_confirmed:
            self.inflect_repo.register_unknown_name(account.name)
        if not self.inflect_repo.get_inflection_by_family_name(
            family_name=account.family_name,
        ).is_confirmed:
            self.inflect_repo.register_unknown_family_name(account.family_name)
        if not self.inflect_repo.get_inflection_by_father_name(
            father_name=account.father_name,
        ).is_confirmed:
            self.inflect_repo.register_unknown_father_name(account.father_name)

    def inflect_account_fio(self, account: Account | Participant) -> str:
        if not self.is_fio_confirmed(account):
            self.register_uninflected_parts(account)
            logger.warning(f"Inflection is not confirmed for {account}")
        name_inflection = self.inflect_repo.get_inflection_by_name(
            name=account.name,
        )
        family_name_inflection = self.inflect_repo.get_inflection_by_family_name(
            family_name=account.family_name,
        )
        father_name_inflection = self.inflect_repo.get_inflection_by_father_name(
            father_name=account.father_name,
        )
        return " ".join(
            [
                family_name_inflection.datv,
                name_inflection.datv,
                father_name_inflection.datv,
            ],
        )
