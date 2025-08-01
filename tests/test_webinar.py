from datetime import date
from unittest.mock import patch

import pytest

from lib.clients.email import EmailTestClient
from lib.domain.certificate.service import CertificateService
from lib.domain.contact.repository import VCardRepository
from lib.domain.contact.service import ContactService
from lib.domain.email.service import EmailService
from lib.domain.webinar.enums import WebinarTitle
from lib.participants import Participant
from lib.sheets import Sheet
from lib.webinar import Webinar
from tests.common import TEST_SHEET_URL
from tests.common import CreateDocumentT


def test_webinar_integration(
    create_document: CreateDocumentT,
    tmp_path_factory,
    create_row,
) -> None:
    # TODO: split test into steps
    contact_tmp_path = tmp_path_factory.mktemp("contacts")
    contact_service = ContactService(
        vcard_repo=VCardRepository(
            path=contact_tmp_path,
        ),
    )
    size = 2
    rows = [create_row() for _ in range(size)]
    participants = [Participant.from_row_v2(row) for row in rows]
    started_at = date(2024, 12, 31)
    finished_at = date(2025, 1, 1)
    document = create_document(rows)
    email_client = EmailTestClient()
    email_service = EmailService(
        email_client=email_client,
        bcc_emails=("abc@abc.com",),
        send_timeout_sec=0,
    )
    sheet = Sheet(document)  # type: ignore[arg-type]
    webinar = Webinar(
        sheet=sheet,
        participants=participants,
        title=WebinarTitle.TEST,
        started_at=started_at,
        finished_at=finished_at,
        certificate_service=CertificateService(),
        contact_service=contact_service,
        email_service=email_service,
    )
    # prepare certificates
    webinar.prepare_emails()

    # send emails
    webinar.send_emails_with_certificates()
    for participant in participants:
        assert email_client.is_sent_to(participant.email)
    assert email_client.total_send_count == len(rows)

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
    group_expected = f"тест {finished_at.isoformat()}"
    path_expected = contact_tmp_path / f"{group_expected}.vcf"
    assert path_expected.exists()
    content = path_expected.read_text()
    assert group_expected in content
    for participant in participants:
        assert participant.family_name in content
        assert participant.name in content
        assert participant.email in content
        assert participant.phone in content


def test_webinar_cen_be_created_from_url(
    monkeypatch: pytest.MonkeyPatch,
    create_document: CreateDocumentT,
    create_row,
) -> None:
    monkeypatch.setenv("BCC_EMAILS", "a,b")
    monkeypatch.setenv("GMAILACCOUNT", "some@gmail.com")
    monkeypatch.setenv("GMAILAPPLICATIONPASSWORD", "123")
    document = create_document([create_row() for _ in range(2)])
    sheet = Sheet(document)  # type: ignore[arg-type]
    with patch.object(Sheet, Sheet.from_url.__name__, lambda _: sheet):
        webinar = Webinar.from_url(TEST_SHEET_URL)
    webinar.with_test_client()
