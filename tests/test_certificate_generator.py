from datetime import date
from pathlib import Path

import pytest
from PIL import Image

from lib.images import BaseCertificateGenerator
from lib.images import GrammarCertGen
from lib.images import PhraseCertGen
from lib.images import SpeechCertGen
from lib.images import TextCertificateGenerator


@pytest.mark.parametrize(
    "cert_gen_class",
    [
        GrammarCertGen,
        SpeechCertGen,
        PhraseCertGen,
    ],
)
def test_certificate_generates_correct_jpeg_file(
    cert_gen_class: BaseCertificateGenerator,
    tmp_path: Path,
) -> None:
    cert_gen = cert_gen_class.create(
        working_dir=tmp_path,
        started_at=date(2024, 12, 31),
        finished_at=date(2024, 12, 31),
    )
    cert = cert_gen.generate_certificate("Василий Пупкин")
    assert cert.exists()
    Image.open(cert, formats=["jpeg"]).verify()


@pytest.mark.parametrize(
    "cert_gen_class",
    [
        GrammarCertGen,
        SpeechCertGen,
        PhraseCertGen,
    ],
)
def test_if_given_different_names_then_files_are_different(
    cert_gen_class: BaseCertificateGenerator,
    tmp_path: Path,
) -> None:
    cert_gen = cert_gen_class.create(
        working_dir=tmp_path,
        started_at=date(2024, 12, 31),
        finished_at=date(2024, 12, 31),
    )
    cert_a = cert_gen.generate_certificate("Василий Пупкин")
    cert_b = cert_gen.generate_certificate("Пётр Курочки")
    assert str(cert_a) != str(cert_b)
    assert Image.open(cert_a).tobytes() != Image.open(cert_b).tobytes()


@pytest.mark.parametrize(
    "cert_gen_class",
    [
        GrammarCertGen,
        SpeechCertGen,
        PhraseCertGen,
    ],
)
def test_cert_file_is_created_inside_given_directory(
    cert_gen_class: BaseCertificateGenerator,
    tmp_path: Path,
) -> None:
    cert_gen = cert_gen_class.create(
        working_dir=tmp_path,
        started_at=date(2024, 12, 31),
        finished_at=date(2024, 12, 31),
    )
    cert_path = cert_gen.generate_certificate("Пётр Курочки")
    tmp_dir_contents = list(tmp_path.glob("*"))
    assert len(tmp_dir_contents) == 1
    assert cert_path in tmp_dir_contents


@pytest.mark.parametrize(
    "started_at,finished_at,date_expected,year_expected",
    [
        (date(2024, 12, 30), date(2024, 12, 31), "30 - 31 декабря", 2024),
        (date(2024, 12, 30), date(2025, 1, 2), "30 декабря - 2 января", 2025),
    ],
)
def test_certificate_contain_all_given_data(
    tmp_path: Path,
    started_at: date,
    finished_at: date,
    date_expected: str,
    year_expected: int,
) -> None:
    name = "Иванов Иван Иванович"
    cert_gen = TextCertificateGenerator.create(
        working_dir=tmp_path,
        started_at=started_at,
        finished_at=finished_at,
    )
    cert_gen.generate_certificate(name)
    cert_path = tmp_path / name
    assert cert_path.exists()
    content = cert_path.read_text()
    assert name in content
    assert f"{year_expected} г." in content
    assert date_expected in content
