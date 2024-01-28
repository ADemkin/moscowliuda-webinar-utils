# pylint: disable=redefined-builtin,redefined-outer-name
import click

from lib.domain.inflect.repository import InflectRepository

pass_inflect_repository = click.make_pass_decorator(InflectRepository, ensure=True)


@click.group()
def cli() -> None:
    ...


# name group: inflect, list unknown, set, unset


@cli.group(help="inflect, list, set and unset name")
def name() -> None:
    ...


@name.command(name="inflect", help="inflect name")
@pass_inflect_repository
@click.argument("name")
def name_inflect(inflect_repo: InflectRepository, name: str) -> None:
    inflection = inflect_repo.get_inflection_by_name(name.title())
    click.echo(inflection)


@name.command(name="list", help="list unknown names")
@pass_inflect_repository
def name_list(inflect_repo: InflectRepository) -> None:
    inflections = inflect_repo.get_unknown_names()
    for inflection in sorted(inflections):
        click.echo(inflection)


@name.command(name="set", help="set name")
@pass_inflect_repository
@click.argument("name")
@click.argument("datv")
def name_set(inflect_repo: InflectRepository, name: str, datv: str) -> None:
    if click.confirm(f"set {name} > {datv} ?", default=True):
        inflect_repo.set_inflection_by_name(name.title(), datv.title())
    else:
        click.echo("not set")


@name.command(name="unset", help="unset name")
@pass_inflect_repository
@click.argument("name")
def name_unset(inflect_repo: InflectRepository, name: str) -> None:
    if click.confirm(f"unset {name} ?", default=True):
        inflect_repo.set_inflection_by_name(name.title(), None)
    else:
        click.echo("not unset")


# family-name group: inflect, list unknown, set, unset


@cli.group(help="inflect, list, set and unset family_name")
def family_name() -> None:
    ...


@family_name.command(name="inflect", help="inflect family_name")
@pass_inflect_repository
@click.argument("family_name")
def family_name_inflect(inflect_repo: InflectRepository, family_name: str) -> None:
    inflection = inflect_repo.get_inflection_by_family_name(family_name.title())
    click.echo(inflection)


@family_name.command(name="list", help="list unknown family_names")
@pass_inflect_repository
def family_name_list(inflect_repo: InflectRepository) -> None:
    inflections = inflect_repo.get_unknown_family_names()
    for inflection in sorted(inflections):
        click.echo(inflection)


@family_name.command(name="set", help="set family_name")
@pass_inflect_repository
@click.argument("family_name")
@click.argument("datv")
def family_name_set(
    inflect_repo: InflectRepository,
    family_name: str,
    datv: str,
) -> None:
    if click.confirm(f"set {family_name} > {datv} ?", default=True):
        inflect_repo.set_inflection_by_family_name(family_name.title(), datv.title())
    else:
        click.echo("not set")


@family_name.command(name="unset", help="unset family_name")
@pass_inflect_repository
@click.argument("family_name")
def family_name_unset(inflect_repo: InflectRepository, family_name: str) -> None:
    if click.confirm(f"unset {family_name} ?", default=True):
        inflect_repo.set_inflection_by_family_name(family_name.title(), None)
    else:
        click.echo("not unset")


# father-name group: inflect, list unknown, set, unset


@cli.group(help="inflect, list, set and unset father_name")
def father_name() -> None:
    ...


@father_name.command(name="inflect", help="inflect father_name")
@pass_inflect_repository
@click.argument("father_name")
def father_name_inflect(inflect_repo: InflectRepository, father_name: str) -> None:
    inflection = inflect_repo.get_inflection_by_father_name(father_name.title())
    click.echo(inflection)


@father_name.command(name="list", help="list unknown father_names")
@pass_inflect_repository
def father_name_list(inflect_repo: InflectRepository) -> None:
    inflections = inflect_repo.get_unknown_father_names()
    for inflection in sorted(inflections):
        click.echo(inflection)


@father_name.command(name="set", help="set father_name")
@pass_inflect_repository
@click.argument("father_name")
@click.argument("datv")
def father_name_set(inflect_repo: InflectRepository, father_name: str, datv: str) -> None:
    if click.confirm(f"set {father_name} > {datv} ?", default=True):
        inflect_repo.set_inflection_by_father_name(father_name.title(), datv.title())
    else:
        click.echo("not set")


@father_name.command(name="unset", help="unset father_name")
@pass_inflect_repository
@click.argument("father_name")
def father_name_unset(inflect_repo: InflectRepository, father_name: str) -> None:
    if click.confirm(f"unset {father_name} ?", default=True):
        inflect_repo.set_inflection_by_father_name(father_name.title(), None)
    else:
        click.echo("not unset")


if __name__ == "__main__":
    cli()
