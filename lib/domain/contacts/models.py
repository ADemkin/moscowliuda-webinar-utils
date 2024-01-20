from dataclasses import dataclass

_TEMPLATE = """BEGIN:VCARD
VERSION:3.0
PRODID:-//Apple Inc.//macOS 13.2.1//EN
N:{first_name};{last_name};;;
FN:{last_name} {first_name}
ORG:{organisation};
EMAIL;type=INTERNET;type=HOME;type=pref:{email}
TEL;type=CELL;type=VOICE;type=pref:{phone}
END:VCARD"""


@dataclass(frozen=True, slots=True)
class VCard:
    first_name: str
    last_name: str
    email: str
    phone: str
    organisation: str

    def to_vcf(self) -> str:
        return _TEMPLATE.format(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            organisation=self.organisation,
        )
