import click
from dotenv import load_dotenv

from lib.domain.email.service import EmailService
from lib.webinar import Webinar


@click.group()
def cli() -> None:
    load_dotenv()


@cli.command()
@click.argument("url")
def contacts(url: str) -> None:
    path = Webinar.from_url(url).import_contacts()
    click.launch(str(path.parent))


@cli.command()
@click.argument("url")
def fill(url: str) -> None:
    Webinar.from_url(url).certificates_sheet_fill()


@cli.command()
@click.argument("url")
@click.option("--test", is_flag=True, default=False)
def send(url: str, test: bool) -> None:  # noqa: FBT001
    webinar = Webinar.from_url(url)
    if test:
        webinar = webinar.with_test_client()
    webinar.from_url(url).send_emails_with_certificates()


if __name__ == "__main__":
    cli()
