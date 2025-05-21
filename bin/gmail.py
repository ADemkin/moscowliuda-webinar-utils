import click
from dotenv import load_dotenv

from lib.domain.email.service import EmailService


@click.group()
def cli() -> None:
    load_dotenv()


@cli.command()
def test() -> None:
    email_service = EmailService()
    email_service.send_email(
        title="Test",
        email=email_service.bcc_emails[0],
        message="This is a test email.",
    )


if __name__ == "__main__":
    cli()
