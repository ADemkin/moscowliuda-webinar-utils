from pathlib import Path
from typing import cast

import pytest

from images import Certificate

TEMPLATE = Path("tests/test_template.jpeg")


def test_cerificate_generate_certificate(tmp_path: Path) -> None:
    name = "Имя Фамилия Отчество"
    date = "40-41 феврабля"
    year = 2020
    cert = Certificate.create(
        template=TEMPLATE,
        certs_dir=tmp_path,
        name=name,
        date=date,
        year=year,
    )
    cert.create_file()
    assert cert.exists()
    assert cert.path == (tmp_path / name).with_suffix(".jpeg")


def test_certificate_gives_error_if_template_not_exitts() -> None:
    path = Path("/random/path/that/does/not/exist")
    assert not path.exists()
    with pytest.raises(RuntimeError) as err:
        Certificate.create(
            template=path,
            certs_dir=cast(Path, 'does-not-matter'),
            name='does-not-matter',
            date='does-not-matter',
            year='does-not-matter',
        )
    err_expected = f"{str(path)} not exists"
    assert str(err.value) == err_expected
