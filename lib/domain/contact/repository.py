from typing import Sequence
from functools import partial
from pathlib import Path
from dataclasses import dataclass, field

from lib.domain.contact.models import VCard


@dataclass(frozen=True, slots=True)
class VCardRepository:
    path: Path = field(default_factory=partial(Path, "contacts"))

    def save_vcards_to_file(self, vcards: Sequence[VCard], group: str) -> Path:
        path = self.path / f"{group}.vcf"
        with open(path, "w", encoding="utf-8") as fd:
            fd.write("\n".join([vcard.to_vcf() for vcard in vcards]))
            fd.flush()
        return path
