import pytest

from factory import get_cert_gen_from_webinar_title
from factory import WebinarTitles
from images import BaseCertificateGenerator
from images import GrammarCertGen
from images import SpeechCertGen
from images import TextCertificateGenerator


@pytest.mark.parametrize("title,cert_gen_class", [
    ("Формирование базовых грамматических представлений", GrammarCertGen),
    ("Формирование Базовых Грамматических Представлений", GrammarCertGen),
    (WebinarTitles.GRAMMAR, GrammarCertGen),
    ("практика запуска речи", SpeechCertGen),
    ("Практика Запуска Речи", SpeechCertGen),
    (WebinarTitles.SPEECH, SpeechCertGen),
    ("Test Webinar", TextCertificateGenerator),
    ("test webinar", TextCertificateGenerator),
    (WebinarTitles.TEST, TextCertificateGenerator),
])
def test_if_given_correct_title_then_gives_corresponding_cert_gen(
    title: str,
    cert_gen_class: BaseCertificateGenerator,
) -> None:
    assert get_cert_gen_from_webinar_title(title) == cert_gen_class
