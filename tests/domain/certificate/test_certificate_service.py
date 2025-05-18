from datetime import date
from io import BytesIO

import pytest
from PIL import Image

from lib.domain.certificate import Certificate
from lib.domain.certificate import CertificateService
from lib.domain.certificate import CertificateTextSerializer
from lib.domain.webinar.enums import WebinarTitle
from lib.utils import date_range_to_text


@pytest.mark.parametrize(
    ("started_at", "finished_at"),
    [
        (date(2021, 1, 1), date(2021, 1, 2)),
        (date(2021, 2, 1), date(2021, 3, 2)),
        (date(2021, 4, 1), date(2021, 5, 1)),
        (date(2021, 6, 1), date(2021, 6, 1)),
        (date(2021, 8, 1), date(2021, 9, 1)),
        (date(2021, 10, 1), date(2021, 11, 1)),
        (date(2021, 12, 31), date(2022, 1, 1)),
    ],
)
@pytest.mark.parametrize("title", list(WebinarTitle))
@pytest.mark.parametrize(
    "name",
    [
        "Мельникова Людмила Андреевна",
        "Мельникова-Дёмкина Людмила Андреевна",
        "Ким Алла Кимовна",
    ],
)
def test_certificate_service_generates_certificate(
    started_at: date,
    finished_at: date,
    title: WebinarTitle,
    name: str,
) -> None:
    service = CertificateService()
    certificate = service.generate(
        title=title,
        started_at=started_at,
        finished_at=finished_at,
        name=name,
    )
    assert certificate.title == title
    assert certificate.name == name
    assert certificate.started_at == started_at
    assert certificate.finished_at == finished_at


@pytest.mark.parametrize(
    ("started_at", "finished_at"),
    [
        (date(2021, 1, 1), date(2021, 1, 2)),
        (date(2021, 2, 1), date(2021, 3, 2)),
        (date(2021, 4, 1), date(2021, 5, 1)),
        (date(2021, 6, 1), date(2021, 6, 1)),
        (date(2021, 8, 1), date(2021, 9, 1)),
        (date(2021, 10, 1), date(2021, 11, 1)),
        (date(2021, 12, 31), date(2022, 1, 1)),
    ],
)
@pytest.mark.parametrize("title", list(WebinarTitle))
@pytest.mark.parametrize(
    "name",
    [
        "Мельникова Людмила Андреевна",
        "Мельникова-Дёмкина Людмила Андреевна",
        "Ким Алла Кимовна",
    ],
)
def test_certificate_contains_correct_text(
    started_at: date,
    finished_at: date,
    title: WebinarTitle,
    name: str,
) -> None:
    certificate = Certificate(
        title=title,
        name=name,
        started_at=started_at,
        finished_at=finished_at,
        serializer=CertificateTextSerializer(),
    )
    buffer = BytesIO()
    certificate.write(buffer)
    text = buffer.getvalue().decode("utf-8")
    assert name in text
    assert title.long() in text
    formatted_date_range = date_range_to_text(
        started_at=started_at,
        finished_at=finished_at,
    )
    assert formatted_date_range in text


def test_serialized_certificate_can_be_decoded_as_png_image() -> None:
    certificate = Certificate(
        title=WebinarTitle.TEST,
        name="Мельникова Людмила Андреевна",
        started_at=date(2025, 1, 3),
        finished_at=date(2025, 1, 4),
    )
    buffer = BytesIO()
    certificate.write(buffer)
    buffer.seek(0)
    image = Image.open(buffer)
    assert image.format == "PNG"
