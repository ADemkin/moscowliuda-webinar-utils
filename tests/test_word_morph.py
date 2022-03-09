import pytest

from tests.common import MorpherT


@pytest.mark.parametrize("fio,fio_given", [
    ('Пупкин Василий Александрович', 'Пупкину Василию Александровичу'),
    ('Качалова Анастасия Валерьевна', 'Качаловой Анастасии Валерьевне'),
    ('Корячкин Андрей Иванович', 'Корячкину Андрею Ивановичу'),
    ('Мельникова Людмила Андреевна', 'Мельниковой Людмиле Андреевне'),
    ('Мазаев Антон Андреевич', 'Мазаеву Антону Андреевичу'),
])
def test_name_changes_to_given_form(
        fio: str,
        fio_given: str,
        morpher: MorpherT,
) -> None:
    assert morpher(fio) == fio_given
