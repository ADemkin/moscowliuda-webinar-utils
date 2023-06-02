from pathlib import Path

import pytest
from PIL import Image

from lib.images import BaseCertificateGenerator
from lib.images import GrammarCertGen
from lib.images import SpeechCertGen
from lib.images import TextCertificateGenerator


@pytest.mark.parametrize("cert_gen_class", [
    GrammarCertGen,
    SpeechCertGen,
])
def test_certificate_generates_correct_jpeg_file(
        cert_gen_class: BaseCertificateGenerator,
        tmp_path: Path,
) -> None:
    cert_gen = GrammarCertGen.create(
        working_dir=tmp_path,
        date="20-21 сентября",
        year=2022,
    )
    cert = cert_gen.generate_cerificate("Василий Пупкин")
    assert cert.exists()
    Image.open(cert, formats=["jpeg"]).verify()


@pytest.mark.parametrize("cert_gen_class", [
    GrammarCertGen,
    SpeechCertGen,
])
def test_if_given_different_names_then_files_are_different(
        cert_gen_class: BaseCertificateGenerator,
        tmp_path: Path,
) -> None:
    cert_gen = GrammarCertGen.create(
        working_dir=tmp_path,
        date="20-21 сентября",
        year=2022,
    )
    cert_a = cert_gen.generate_cerificate("Василий Пупкин")
    cert_b = cert_gen.generate_cerificate("Пётр Курочки")
    assert str(cert_a) != str(cert_b)
    assert Image.open(cert_a).tobytes() != Image.open(cert_b).tobytes()


@pytest.mark.parametrize("cert_gen_class", [
    GrammarCertGen,
    SpeechCertGen,
])
def test_cert_file_is_created_inside_given_directory(
        cert_gen_class: BaseCertificateGenerator,
        tmp_path: Path,
) -> None:
    cert_gen = GrammarCertGen.create(
        working_dir=tmp_path,
        date="20-21 сентября",
        year=2022,
    )
    cert_path = cert_gen.generate_cerificate("Пётр Курочки")
    tmp_dir_contents = [f for f in tmp_path.glob("*")]
    assert len(tmp_dir_contents) == 1
    assert cert_path in tmp_dir_contents


def test_certificate_contain_all_given_data(tmp_path: Path) -> None:
    name = "Иванов Иван Иванович"
    date = "26-27 февраля"
    year = 2022
    cert_gen = TextCertificateGenerator.create(tmp_path, date, year)
    cert_gen.generate_cerificate(name)
    cert_path = tmp_path / name
    assert cert_path.exists()
    content = cert_path.read_text()
    assert name in content
    assert f"{year} г." in content
    assert date in content
