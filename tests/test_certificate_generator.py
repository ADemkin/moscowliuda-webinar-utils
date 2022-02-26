from pathlib import Path

import pytest

from images import BaseCertificateGenerator
from images import get_cert_gen_from_webinar_title
from images import GrammarCertGen
from images import SpeechCertGen
from images import TextGrammarCertGen
from images import TextSpeechCertGen
from PIL import Image

TEMPLATE = Path("tests/test_template.jpeg")


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


@pytest.mark.parametrize("title_and_cert_gen_class", [
    ("Формирование базовых грамматических представлений", GrammarCertGen),
    ("Формирование Базовых Грамматических Представлений", GrammarCertGen),
    ("практика запуска речи", SpeechCertGen),
    ("Практика Запуска Речи", SpeechCertGen),
])
def test_if_given_correct_title_then_gives_corresponding_cert_gen(
    title_and_cert_gen_class: tuple[str, BaseCertificateGenerator],
) -> None:
    title, cert_gen_class = title_and_cert_gen_class
    assert get_cert_gen_from_webinar_title(title) == cert_gen_class


@pytest.mark.parametrize("cert_gen_class", [
    TextGrammarCertGen,
    TextSpeechCertGen,
])
def test_certificate_contain_all_given_data(
        cert_gen_class: BaseCertificateGenerator,
        tmp_path: Path,
) -> None:
    name = "Иванов Иван Иванович"
    date = "26-27 февраля"
    year = 2022
    cert_gen = cert_gen_class.create(tmp_path, date, year)
    cert_gen.generate_cerificate(name)
    cert_path = tmp_path / name
    assert cert_path.exists()
    content = cert_path.read_text()
    assert name in content
    assert f"{year} г." in content
    assert date in content
