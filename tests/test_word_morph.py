import pytest

from word_morph import Morph
from word_morph import WordMorphError


@pytest.mark.parametrize("fio,fio_given,just_name", [
    (
        'Пупкин Василий Александрович',
        'Пупкину Василию Александровичу',
        'Василий',
    ),
    (
        'Качалова Анастасия Валерьевна',
        'Качаловой Анастасии Валерьевне',
        'Анастасия',
    ),
])
def test_name_changes_to_given_form(
        fio: str,
        fio_given: str,
        just_name: str,
) -> None:
    morph = Morph.from_fio(fio)
    assert morph.fio == fio
    assert morph.fio_given == fio_given
    assert morph.name == just_name


def test_if_not_russian_input_then_raises() -> None:
    with pytest.raises(WordMorphError) as err:
        Morph.from_fio("not in russian")
    err_expected = "Status 496: 'Не найдено русских слов.'"
    assert str(err.value) == err_expected, err.value
