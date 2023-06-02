from pathlib import Path

TEMPLATE = """BEGIN:VCARD
VERSION:3.0
PRODID:-//Apple Inc.//macOS 13.2.1//EN
N:{first_name};{last_name};;;
FN:{last_name} {first_name}
ORG:{organisation};
EMAIL;type=INTERNET;type=HOME;type=pref:{email}
TEL;type=CELL;type=VOICE;type=pref:{phone}
END:VCARD"""


def create_vcard(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    organisation: str,
) -> str:
    """Encode single vcard as string."""
    return TEMPLATE.format(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        organisation=organisation,
    )


def save_vcards_to_file(path: Path | str, vcards: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as fd:
        vcards_join = "\n".join(vcards)
        fd.write(vcards_join)
        fd.flush()
