from os import listdir
from unittest.mock import patch

import pytest

from lib.clients.email import MailStub
from lib.domain.contact.repository import VCardRepository
from lib.domain.contact.service import ContactService
from lib.domain.inflect.service import InflectService
from lib.domain.webinar.enums import WebinarTitle
from lib.images import TextCertificateGenerator
from lib.participants import Participant
from lib.webinar import Webinar
from tests.common import TEST_SHEET_URL
from tests.common import CreateDocumentT
from tests.common import create_row
from tests.common import skip_if_no_network


@pytest.fixture
def _no_sleep():
    with patch("lib.webinar.sleep"):
        yield


@skip_if_no_network
def test_webinar_integration(  # pylint: disable=too-many-locals
    create_document: CreateDocumentT,
    tmp_path_factory,
    _no_sleep,
) -> None:
    # TODO: split test into steps
    webinar_tmp_path = tmp_path_factory.mktemp("webinar")
    contact_tmp_path = tmp_path_factory.mktemp("contacts")
    contact_service = ContactService(
        vcard_repo=VCardRepository(
            path=contact_tmp_path,
        ),
    )
    rows = [
        create_row("Мазаев", "Антон", "Андреевич", email="a@ya.ru"),
        create_row("Мельникова", "Людмила", "Андреевна", email="l@ya.ru"),
    ]
    participants = [Participant.from_row(row) for row in rows]
    document = create_document(rows)
    date_str = "00-99 Month"
    year = 2022
    mail = MailStub()
    webinar = Webinar(
        document=document,
        participants=participants,
        title=WebinarTitle.TEST,
        date_str=date_str,
        year=year,
        email=mail,
        cert_gen=TextCertificateGenerator(
            working_dir=webinar_tmp_path,
            date=date_str,
            year=str(year),
        ),
        tmp_dir=webinar_tmp_path,
        contact_service=contact_service,
        inflect_service=InflectService(),
    )

    # generate certificates
    webinar.certificates_sheet_fill()
    webinar.certificates_generate()
    assert len(listdir(webinar_tmp_path)) == len(rows)
    for name in ("Мазаеву Антону Андреевичу", "Мельниковой Людмиле Андреевне"):
        path = webinar_tmp_path / name
        assert path.exists()
        content = path.read_text()
        assert name in content
        # assert title in content
        assert date_str in content
        assert str(year) in content

    # send emails
    webinar.send_emails_with_certificates()
    for participant in participants:
        assert mail.is_sent_to(participant.email)

    # trigger email send again will not send them
    webinar.send_emails_with_certificates()
    for participant in participants:
        assert mail.sent_count(participant.email) == 1
    assert mail.total_send_count == len(rows)
    assert listdir(webinar_tmp_path) == ["certificate.jpeg"]

    # create vcards
    webinar.import_contacts()
    group_expected = f"Т{date_str.replace(' ', '')} {year}"
    path_expected = contact_tmp_path / f"{group_expected}.vcf"
    assert path_expected.exists()
    content = path_expected.read_text()
    assert group_expected in content
    for participant in participants:
        assert participant.family_name in content
        assert participant.name in content
        assert participant.email in content
        assert participant.phone in content


@skip_if_no_network
def test_webinar_cen_be_created_from_url(
    create_document: CreateDocumentT,
) -> None:
    rows = [
        create_row("Мазаев", "Антон", "Андреевич", email="a@ya.ru"),
        create_row("Мельникова", "Людмила", "Андреевна", email="l@ya.ru"),
    ]
    create_document(rows)
    Webinar.from_url(TEST_SHEET_URL, test=True)
