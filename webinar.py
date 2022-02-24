from datetime import datetime
from pathlib import Path
from time import sleep

from gspread import Spreadsheet
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound

from images import Certificate
from loguru import logger
from participants import Participant
from send_email import AbstractMail
from send_email import GMail
from send_email import MailStub
from sheets import get_participants_from_sheet
from sheets import get_webinar_date_and_title
from sheets import open_spreadsheet
from word_morph import Morph


URL = (
    "https://docs.google.com/spreadsheets/d/"
    "18k_3stoWisJEzebVbnqcviJgLZsYmy_WFpNSgWc-QSc"
)
URL = "https://docs.google.com/spreadsheets/d/1mj6-i4uC5HM_v-WLB3jgo22SvruULnawCNxlkGgWDIU/edit?usp=sharing"
CERTIFICATES = "mailing"
PARTICIPANTS = "Form Responses 1"


class Webinar:
    def __init__(
            self,
            document: Spreadsheet,
            participants: list[Participant],
            title: str,
            date_str: str,
            year: int,
            certs_dir: Path,
            cert_template: Path,
            email: AbstractMail,
    ) -> None:
        self.document: Spreadsheet = document
        self.participants: list[Participant] = participants
        self.title: str = title
        self.date_str: str = date_str
        self.year: int = year
        self._cert_sheet: Worksheet = None
        self.certs_dir = certs_dir
        self.cert_template = cert_template
        self.email = email

    @classmethod
    def from_url(cls, url: str = URL) -> 'Webinar':
        document = open_spreadsheet(url)
        logger.debug("creating webinar")
        # get participants
        participants = get_participants_from_sheet(
            document.worksheet(PARTICIPANTS),
            first_row=1,
        )
        # get title and date
        date_str, title = get_webinar_date_and_title(document)
        year = datetime.now().year
        # get certificates data
        # cert_template = Path("template_speech.jpeg")
        cert_template = Path("template_grammar.jpeg")
        certs_parent_dir = Path('.') / 'certificates'
        certs_parent_dir.mkdir(exist_ok=True)
        certs_dir = certs_parent_dir / f"{date_str}-{year}"
        certs_dir.mkdir(exist_ok=True)
        # create mailer
        # email = MailStub()
        email = GMail.from_environ()
        return cls(
            document=document,
            participants=participants,
            title=title,
            date_str=date_str,
            year=year,
            certs_dir=certs_dir,
            cert_template=cert_template,
            email=email,
        )

    def _is_sheet_filled(self, sheet_name: str) -> bool:
        values = self.document.worksheet(sheet_name).get_all_values()
        return len(values) == len(self.participants)

    @property
    def cert_sheet(self) -> Worksheet:
        headers = ['fio', 'given_fio', 'name', 'email', 'custom_text']
        # TODO: add instagram after email

        if self._cert_sheet is None:
            try:
                self._cert_sheet = self.document.worksheet(CERTIFICATES)
            except WorksheetNotFound:
                logger.info("creating certificates sheet")
                self._cert_sheet = self.document.add_worksheet(
                    title=CERTIFICATES,
                    rows=len(self.participants),
                    cols=len(headers),
                )
                logger.info("done")
        return self._cert_sheet

    def certificates_sheet_is_filled(self) -> bool:
        cert_sheet_rows = self.cert_sheet.get_all_values()
        if len(cert_sheet_rows) == len(self.participants):
            logger.debug("already filled")
            return True
        elif len(cert_sheet_rows) > len(self.participants):
            logger.warning("already filled but rows > participants")
            return True
        elif 0 < len(cert_sheet_rows) < len(self.participants):
            logger.error("looks like table is filled up partially")
        return False

    def certificates_sheet_fill(self) -> None:
        logger.info("filling certificates")
        if self.certificates_sheet_is_filled():
            return
        for participant in self.participants:
            # TODO: check if participant already in table
            logger.info(f"{participant.fio} taken")
            try:
                morph = Morph.from_fio(participant.fio)
                logger.info(f"{participant.fio} morphed")
                fio_given = morph.fio_given
                name = morph.name
            except Exception as err:
                logger.exception(f"Unable to morph {participant.fio}", err)
                fio_given = ''
                name = ''
            message = f'Здравствуйте, {name}! Благодарю вас за участие.'
            row = [
                participant.fio,
                fio_given,
                name,
                participant.email,
                message,
            ]
            self.cert_sheet.append_row(row)
            logger.info(f"{participant.fio} done")
        logger.info("filling certificates done")

    def certificates_generate(self) -> None:
        logger.info("generating certs")
        # TODO: get exact values, even if they are ''
        for row in self.cert_sheet.get_all_values():
            given_fio = row[1]
            logger.debug(f"{given_fio} taken")
            certificate = Certificate.create(
                template=self.cert_template,
                certs_dir=self.certs_dir,
                name=given_fio,
                date=self.date_str,
                year=self.year,
            )
            certificate.create_file()
            logger.debug(f"{given_fio} cert path: {str(certificate.path)}")
        logger.info("generating certs done")

    def send_emails_with_certificates(self) -> None:
        # headers = ['name', 'given_name', 'just_name', 'email', 'custom_text']
        logger.info("sending emails")
        for row in self.cert_sheet.get_all_values():
            fio, given_fio, _, email, message = row
            logger.debug(f"{fio} taken")
            cert = Certificate.create(
                template=self.cert_template,
                certs_dir=self.certs_dir,
                name=given_fio,
                date=self.date_str,
                year=self.year,
            )
            if not cert.exists():
                logger.debug(f"{fio} generating cert")
                cert.create_file()
                logger.debug(f"{fio} generating cert done")
            # message = message.format(name=name)
            logger.info(f"{fio} sending email to {email}")
            # Hack to send files with latin name
            new_file = "/tmp/certificate.jpeg"
            with open(new_file, "wb") as new_fd:
                with open(cert.path, "rb") as old_fd:
                    new_fd.write(old_fd.read())
            self.email.send(
                to=email,
                bcc=["antondemkin+python@yandex.ru", "moscowliuda@mail.ru"],
                subject=self.title,
                contents=message,
                attachments=[new_file],
            )
            logger.info(f"{fio} done")
            # TODO: mark email as sent in google sheet
            sleep(3)
        logger.info("sending emails done")


if __name__ == '__main__':
    print(URL)
    # tonyflexmusic@gmail.com jnrbviavjvpxtogz
    # GMAILACCOUNT="milabaltyca@gmail.com"
    # GMAILAPPLICATIONPASSWORD="ybullixoirpowibr"
    webinar = Webinar.from_url(URL)
    # webinar.certificates_sheet_fill()
    # make sure that names transformed correctly
    # webinar.certificates_generate()
    # make sure that certificates are correct
    # webinar.send_emails_with_certificates()
