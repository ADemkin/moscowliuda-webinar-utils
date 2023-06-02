from lib.contacts import create_vcard


def test_vcard_contains_all_fields():
    first_name = "Anton"
    last_name = "Demkin"
    email = "myemail@mail.com"
    phone = "+7 916 803-58-95"
    organisation = "Family"
    vcard = create_vcard(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        organisation=organisation,
    )
    assert "BEGIN:VCARD" in vcard
    assert first_name in vcard
    assert last_name in vcard
    assert email in vcard
    assert phone in vcard
    assert organisation in vcard
    assert "END:VCARD" in vcard
