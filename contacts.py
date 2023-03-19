def create_vcard(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    organisation: str,
) -> str:
    """Encode single vcard as string."""
    parts = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"ORG:{organisation};",
        f"N:{last_name};{first_name};;;",
        f"TEL:{phone}",
        f"EMAIL:{email}",
        "END:VCARD",
    ]
    return "\n".join(parts)


if __name__ == "__main__":
    group = "TestGroup"
    vcards = [
        create_vcard("Мама", "Семья", "a@e.s", "12341234", group),
        create_vcard("Папа", "Семья", "a@e.s", "12341235", group),
        create_vcard("Я", "Семья", "a@e.s", "12341236", group),
    ]
    with open("test.vcf", "wb") as fd:
        for vcard in vcards:
            fd.write(f"{vcard}\n".encode("utf-8"))
