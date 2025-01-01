import pytest

from lib.domain.webinar.enums import WebinarTitle
from lib.images import BaseCertificateGenerator
from lib.images import GrammarCertGen
from lib.images import PhraseCertGen
from lib.images import SpeechCertGen
from lib.images import TextCertificateGenerator
from lib.images import cert_gen_factory


@pytest.mark.parametrize(
    "title,cert_gen_class",
    [
        (WebinarTitle.GRAMMAR, GrammarCertGen),
        (WebinarTitle.SPEECH, SpeechCertGen),
        (WebinarTitle.PHRASE, PhraseCertGen),
        (WebinarTitle.TEST, TextCertificateGenerator),
    ],
)
def test_if_given_correct_title_then_gives_corresponding_cert_gen(
    title: WebinarTitle,
    cert_gen_class: BaseCertificateGenerator,
) -> None:
    assert cert_gen_factory(title) == cert_gen_class
