from pathlib import Path
from os import listdir

from images import TextCertificateGenerator
from participants import Participant
from send_email import MailStub
from tests.common import create_row
from tests.common import CreateDocumentT
from webinar import Webinar
from word_morph import offline_morph


def test_webinar_generate_certificates_for_given_participants(
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
    for name in ('Мазаеву Антону Андреевичу', 'Мельниковой Людмиле Андреевне'):
        path = tmp_path / name
        assert path.exists()
        content = path.read_text()
        assert name in content
        # assert title in content
        assert date_str in content
        assert str(year) in content
    webinar.send_emails_with_certificates()
    for participant in participants:
        mail_stub.assert_email_sent_to(participant.email)
    assert listdir(tmp_path) == ["certificate.jpeg"]
