from dataclasses import dataclass
from dataclasses import field

from lib.domain.inflect.repository import InflectRepository
from lib.domain.webinar.models import Account
from lib.participants import Participant


@dataclass(frozen=True, slots=True)
class InflectService:
    inflect_repo: InflectRepository = field(default_factory=InflectRepository)

    def inflect_account_fio(self, account: Account | Participant) -> str:
        # TODO: stub code, replace with real logic
        return self.inflect_repo.get_datv_by_name(account.name).datv
