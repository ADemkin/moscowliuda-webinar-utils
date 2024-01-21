# pylint: disable=redefined-builtin,redefined-outer-name
import click

from lib.domain.inflect.repository import InflectRepository


@click.group()
def cli() -> None:
    ...


@cli.group()
def inflect() -> None:
    ...


@inflect.command()
@click.argument("name")
def name(name: str) -> None:
    inflection = InflectRepository().get_inflection_by_name(name.title())
    click.echo(inflection)


@inflect.command()
@click.argument("family_name")
def family_name(family_name: str) -> None:
    inflection = InflectRepository().get_inflection_by_family_name(family_name.title())
    click.echo(inflection)


@inflect.command()
@click.argument("father_name")
def father_name(father_name: str) -> None:
    inflection = InflectRepository().get_inflection_by_father_name(father_name.title())
    click.echo(inflection)


@cli.group(name="list")
def _list() -> None:
    ...


@_list.command()
def names() -> None:
    inflections = InflectRepository().get_unknown_names()
    for inflection in inflections:
        click.echo(repr(inflection))


@_list.command()
def family_names() -> None:
    inflections = InflectRepository().get_unknown_family_names()
    for inflection in inflections:
        click.echo(repr(inflection))


@_list.command()
def father_names() -> None:
    inflections = InflectRepository().get_unknown_father_names()
    for inflection in inflections:
        click.echo(repr(inflection))


@cli.group()
def fill() -> None:
    ...


@fill.command(name="names")
def fill_names() -> None:
    inflect_repo = InflectRepository()
    names = inflect_repo.get_unknown_names()
    click.echo(f"Found {len(names)} unknown names")
    for name in names:
        inflection = inflect_repo.get_inflection_by_name(name)
        datv = inflection.datv
        if not click.confirm(f"is  {name!r} > {datv!r} ?", default=True):
            datv = click.prompt(f"{inflection.base} > ? (? to skip)", type=str)
            if datv == "?":
                continue
        if click.confirm(f"set {name!r} > {datv!r} (n to skip)?", default=True):
            inflect_repo.set_inflection_by_name(name, inflection.datv)


if __name__ == "__main__":
    cli()
