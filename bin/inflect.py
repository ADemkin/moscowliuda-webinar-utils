# pylint: disable=redefined-builtin,redefined-outer-name
import click

from lib.domain.inflect.repository import InflectRepository


@click.group()
def cli() -> None:
    ...


@cli.command()
@click.argument("name")
def name(name: str) -> None:
    inflection = InflectRepository().get_inflection_by_name(name.title())
    click.echo(inflection)


@cli.command()
@click.argument("family_name")
def family_name(family_name: str) -> None:
    inflection = InflectRepository().get_inflection_by_family_name(family_name.title())
    click.echo(inflection)


@cli.command()
@click.argument("father_name")
def father_name(father_name: str) -> None:
    inflection = InflectRepository().get_inflection_by_father_name(father_name.title())
    click.echo(inflection)


@cli.group()
def list() -> None:
    ...


@list.command()
def names() -> None:
    inflections = InflectRepository().get_unknown_names()
    for inflection in inflections:
        click.echo(inflection)


@list.command()
def family_names() -> None:
    inflections = InflectRepository().get_unknown_family_names()
    for inflection in inflections:
        click.echo(inflection)


@list.command()
def father_names() -> None:
    inflections = InflectRepository().get_unknown_father_names()
    for inflection in inflections:
        click.echo(inflection)


if __name__ == "__main__":
    cli()
