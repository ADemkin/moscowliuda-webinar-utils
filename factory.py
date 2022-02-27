from enum import Enum
from enum import unique

from images import BaseCertificateGenerator
from images import GrammarCertGen
from images import SpeechCertGen
from images import TextCertificateGenerator


@unique
class WebinarTitles(Enum):
    grammar = "формирование базовых грамматических представлений"
    speech = "практика запуска речи"
    test = "test webinar"


def get_cert_gen_from_webinar_title(
        title: str | WebinarTitles,
) -> type[BaseCertificateGenerator]:
    if isinstance(title, WebinarTitles):
        title = title.value
    title_to_class = {
        WebinarTitles.grammar.value: GrammarCertGen,
        WebinarTitles.speech.value: SpeechCertGen,
        WebinarTitles.test.value: TextCertificateGenerator,
    }
    if (class_ := title_to_class.get(title.lower())):
        return class_
    raise ValueError(f"Unknown webinar title: {title!r}")
