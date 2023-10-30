from os import listdir
from pathlib import Path

from lib.images import TextCertificateGenerator
from lib.participants import Participant
from lib.send_email import MailStub
from lib.webinar import Webinar
from lib.word_morph import offline_morph
from tests.common import CreateDocumentT
from tests.common import create_row
from tests.common import skip_if_no_network


@skip_if_no_network
def test_webinar_integration(
    create_document: CreateDocumentT,
    tmp_path: Path,
) -> None:
    rows = [
        create_row("Мазаев", "Антон", "Андреевич", email="a@ya.ru"),
        create_row("Мельникова", "Людмила", "Андреевна", email="l@ya.ru"),
    ]
    participants = [Participant.from_row(row) for row in rows]
    document = create_document(rows)
    mail_stub = MailStub()
    title = "Test Webinar"
    date_str = "00-99 Month"
    year = 2022
    webinar = Webinar(
        document=document,
        participants=participants,
        title=title,
        date_str=date_str,
        year=year,
        test_email=mail_stub,
        email=mail_stub,
        cert_gen=TextCertificateGenerator(
            working_dir=tmp_path,
            date=date_str,
            year=str(year),
        ),
        tmp_dir=tmp_path,
        morphological=offline_morph,
    )
    webinar.certificates_sheet_fill()
    webinar.certificates_generate()
    assert len(listdir(tmp_path)) == len(rows)
    for name in ("Мазаеву Антону Андреевичу", "Мельниковой Людмиле Андреевне"):
        path = tmp_path / name
        assert path.exists()
        content = path.read_text()
        assert name in content
        # assert title in content
        assert date_str in content
        assert str(year) in content
    # send emails
    webinar.send_emails_with_certificates()
    for participant in participants:
        mail_stub.assert_email_sent_to(participant.email)
    # trigger email send again will not send them
    webinar.send_emails_with_certificates()
    for participant in participants:
        mail_stub.email_sent_count(participant.email) == 1
    assert listdir(tmp_path) == ["certificate.jpeg"]
