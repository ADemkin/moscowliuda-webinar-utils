import pytest

from lib.domain.webinar.enums import WebinarTitle
from lib.factory import get_cert_gen_from_webinar_title
from lib.images import BaseCertificateGenerator
from lib.images import GrammarCertGen
from lib.images import SpeechCertGen
from lib.images import TextCertificateGenerator


@pytest.mark.parametrize(
    "title,cert_gen_class",
    [
        ("Формирование базовых грамматических представлений", GrammarCertGen),
        ("Формирование Базовых Грамматических Представлений", GrammarCertGen),
        (WebinarTitle.GRAMMAR, GrammarCertGen),
        ("практика запуска речи", SpeechCertGen),
        ("Практика Запуска Речи", SpeechCertGen),
        (WebinarTitle.SPEECH, SpeechCertGen),
        ("Test Webinar", TextCertificateGenerator),
        ("test webinar", TextCertificateGenerator),
        (WebinarTitle.TEST, TextCertificateGenerator),
    ],
)
def test_if_given_correct_title_then_gives_corresponding_cert_gen(
    title: str,
    cert_gen_class: BaseCertificateGenerator,
) -> None:
    assert get_cert_gen_from_webinar_title(title) == cert_gen_class
