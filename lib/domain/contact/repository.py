from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from lib.domain.contact.models import VCard
from lib.paths import ETC_PATH


@dataclass(frozen=True, slots=True)
class VCardRepository:
    path: Path = field(default=ETC_PATH / "contacts")

    def save_vcards_to_file(self, vcards: Sequence[VCard], group: str) -> Path:
        path = self.path / f"{group}.vcf"
        with path.open("w") as fd:
            fd.write("\n".join([vcard.to_vcf() for vcard in vcards]))
            fd.flush()
        return path
