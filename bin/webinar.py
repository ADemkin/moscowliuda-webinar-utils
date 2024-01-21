import click
from dotenv import load_dotenv

from lib.domain.webinar.service import WebinarService
from lib.webinar import Webinar


@click.group()
def cli() -> None:
    load_dotenv()


@cli.command()
@click.argument("url")
def contacts(url: str) -> None:
    click.echo(f"Importing contacts from {url}")
    click.confirm("Continue?", default=True, abort=True)
    path = Webinar.from_url(url).import_contacts()
    click.echo(f"Contacts saved to {click.format_filename(path)}")
    click.echo("Import this file using icloud.com")
    if click.confirm("Open directory with contacts?", default=True):
        click.launch(str(path.parent))


@cli.command()
@click.argument("url")
def fill(url: str) -> None:
    click.echo(f"Fill mailing sheet from {url}")
    click.confirm("Continue?", default=True, abort=True)
    Webinar.from_url(url).certificates_sheet_fill()
    click.echo("Mailing sheet filled")
    if click.confirm("Open mailing sheet?", default=True):
        click.launch(url)


@cli.command()
@click.argument("url")
def send(url: str) -> None:
    click.echo(f"Send emails with certificates from {url}")
    if click.confirm("Open mailing sheet?", default=True):
        click.launch(url)
    if click.confirm("Test emails?", default=True):
        Webinar.from_url(url, test=True).send_emails_with_certificates()
    if click.confirm(click.style("Send emails?", fg="red"), abort=True):
        Webinar.from_url(url).send_emails_with_certificates()
        click.echo("Emails sent")


@cli.command(name="import")
@click.argument("url")
def _import(url: str) -> None:
    click.echo(f"Importing webinar from {url}")
    accounts = WebinarService().import_webinar_and_accounts_by_url(url)
    click.echo(f"{len(accounts)} accounts imported")


if __name__ == "__main__":
    cli()
