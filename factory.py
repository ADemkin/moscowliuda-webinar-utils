from enum import Enum, unique

from images import (
    BaseCertificateGenerator,
    GrammarCertGen,
    SpeechCertGen,
    TextCertificateGenerator,
)


@unique
class WebinarTitles(Enum):
    GRAMMAR = "формирование базовых грамматических представлений"
    SPEECH = "практика запуска речи"
    TEST = "test webinar"


def get_cert_gen_from_webinar_title(
    title: str | WebinarTitles,
) -> type[BaseCertificateGenerator]:
    if isinstance(title, WebinarTitles):
        title = title.value
    title_to_class = {
        WebinarTitles.GRAMMAR.value: GrammarCertGen,
        WebinarTitles.SPEECH.value: SpeechCertGen,
        WebinarTitles.TEST.value: TextCertificateGenerator,
    }
    if class_ := title_to_class.get(title.lower()):
        return class_
    raise ValueError(f"Unknown webinar title: {title!r}")
