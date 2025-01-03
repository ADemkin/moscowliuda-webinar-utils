from datetime import date
from unittest.mock import patch

import pytest

from lib.clients.email import TestEmailClient
from lib.domain.certificate.service import CertificateService
from lib.domain.contact.repository import VCardRepository
from lib.domain.contact.service import ContactService
from lib.domain.email.service import EmailService
from lib.domain.webinar.enums import WebinarTitle
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
    contact_tmp_path = tmp_path_factory.mktemp("contacts")
    email_tmp_path = tmp_path_factory.mktemp("email")
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
    started_at = date(2024, 12, 31)
    finished_at = date(2025, 1, 1)
    document = create_document(rows)
    email_client = TestEmailClient()
    email_service = EmailService(
        email_client=email_client,
        bcc_emails=("abc@abc.com",),
        tmp_path=email_tmp_path,
    )
    certificate_service = CertificateService(
        title=WebinarTitle.TEST,
        started_at=started_at,
        finished_at=finished_at,
    )
    webinar = Webinar(
        document=document,
        participants=participants,
        title=WebinarTitle.TEST,
        started_at=started_at,
        finished_at=finished_at,
        certificate_service=certificate_service,
        contact_service=contact_service,
        email_service=email_service,
    )
    # prepare certificates
    webinar.certificates_sheet_fill()

    # send emails
    webinar.send_emails_with_certificates()
    for participant in participants:
        assert email_client.is_sent_to(participant.email)

    # trigger email send again will not send them
    webinar.send_emails_with_certificates()
    for participant in participants:
        email = participant.email
        assert email_client.is_sent_to(email)
        assert email_client.sent_count(email) == 1
        attach = email_client.get_attachments(email)
        assert len(attach) == 1
    assert email_client.total_send_count == len(rows)

    # create vcards
    webinar.import_contacts()
    group_expected = f"Т{finished_at.isoformat()}"
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
    monkeypatch: pytest.MonkeyPatch,
    create_document: CreateDocumentT,
) -> None:
    monkeypatch.setenv("BCC_EMAILS", "a,b")  # not checked
    rows = [
        create_row("Мазаев", "Антон", "Андреевич", email="a@ya.ru"),
        create_row("Мельникова", "Людмила", "Андреевна", email="l@ya.ru"),
    ]
    create_document(rows)
    Webinar.from_url(TEST_SHEET_URL, test=True)
