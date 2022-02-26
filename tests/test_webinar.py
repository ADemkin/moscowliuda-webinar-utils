import pytest

from tests.common import create_row


def test_webinar(create_sheet: any) -> None:
    create_sheet(rows=[
        create_row("Мазаев", "Антон", "Андреевич"),
        create_row("Мельникова", "Людмила", "Андреевна"),
    ])
