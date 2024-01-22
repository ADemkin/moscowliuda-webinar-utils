from lib.domain.webinar.enums import WebinarTitle
from lib.images import BaseCertificateGenerator
from lib.images import GrammarCertGen
from lib.images import SpeechCertGen
from lib.images import TextCertificateGenerator


def get_cert_gen_from_webinar_title(
    title: str | WebinarTitle,
) -> type[BaseCertificateGenerator]:
    # cast str to calm down mypy- it thinks that we need to overload .get method
    title_to_class = {
        str(WebinarTitle.SPEECH): SpeechCertGen,
        str(WebinarTitle.TEST): TextCertificateGenerator,
        str(WebinarTitle.GRAMMAR): GrammarCertGen,
    }
    if generator_class := title_to_class.get(title.lower()):
        return generator_class
    raise ValueError(f"Unknown webinar title: {title!r}")
