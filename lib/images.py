from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lib.const import MONTH2NAME
from lib.domain.webinar.enums import WebinarTitle
from lib.paths import ETC_PATH

BLACK = (0, 0, 0)


@dataclass
class RelativePosition:
    width: float
    height: float

    def __mul__(self, other: tuple[int]) -> tuple[float, float]:
        if len(other) != 2:
            raise ValueError(f"expecting exactly 2 items, got {len(other)}")
        return (other[0] * self.width, other[1] * self.height)  # type: ignore


MAX_TEXT_SIZE = RelativePosition(width=0.8, height=0.5)
TEXT_POSITION = RelativePosition(width=0.50, height=0.61)
DATE_POSITION = RelativePosition(width=0.40, height=0.69)
YEAR_POSITION = RelativePosition(width=0.40, height=0.72)
FONT = "Helvetica"
MIN_FONT_SIZE = 20
MAX_FONT_SIZE = 35
DATE_FONT_SIZE = 35


@lru_cache(maxsize=MAX_FONT_SIZE - MIN_FONT_SIZE)
def get_font(size: int = 10) -> ImageFont:
    return ImageFont.truetype(FONT, size=size)


def get_max_text_size(image: Image) -> tuple[float, float]:
    return MAX_TEXT_SIZE * image.size


def get_text_position(image: Image) -> tuple[float, float]:
    return TEXT_POSITION * image.size


def get_date_position(image: Image) -> tuple[float, float]:
    return DATE_POSITION * image.size


def get_year_position(image: Image) -> tuple[float, float]:
    return YEAR_POSITION * image.size


def calculate_largest_font_size_for_text(image: Image, text: str) -> ImageFont:
    max_text_size = get_max_text_size(image)
    for font_size in range(MIN_FONT_SIZE, MAX_FONT_SIZE):
        font = get_font(size=font_size)
        if font.getsize_multiline(text) > max_text_size:
            break
    return font_size


def create_certificate(
    template: Path,
    name: str,
    date_text: str,
    year_text: str,
) -> Image:
    with Image.open(template) as image:
        # fill name
        ImageDraw.Draw(image).multiline_text(
            xy=get_text_position(image),
            font=get_font(calculate_largest_font_size_for_text(image, name)),
            text=name,
            anchor="ma",  # middle & top edge is anchor point
            fill=BLACK,
        )
        # fill webinar date
        ImageDraw.Draw(image).multiline_text(
            xy=get_date_position(image),
            font=get_font(DATE_FONT_SIZE),
            text=date_text,
            anchor="ma",  # middle & top edge is anchor point
            fill=BLACK,
        )
        # fill webinar year
        ImageDraw.Draw(image).multiline_text(
            xy=get_year_position(image),
            font=get_font(DATE_FONT_SIZE),
            text=year_text,
            anchor="ma",  # middle & top edge is anchor point
            fill=BLACK,
        )
        return image


class BaseCertificateGenerator:
    _templates_dir: Path = ETC_PATH / "templates"
    template: str = ""

    def __init__(
        self,
        working_dir: Path,
        started_at: date,
        finished_at: date,
    ) -> None:
        self._working_dir = working_dir
        self._started_at = started_at
        self._finished_at = finished_at

    @classmethod
    def create(
        cls,
        working_dir: Path,
        started_at: date,
        finished_at: date,
    ) -> "BaseCertificateGenerator":
        return cls(
            working_dir=working_dir,
            started_at=started_at,
            finished_at=finished_at,
        )

    @property
    def _template_path(self) -> Path:
        return self._templates_dir / self.template

    def _get_year_text(self) -> str:
        return f"{self._finished_at.year} г."

    def _get_date_text(self) -> str:
        finish_month = MONTH2NAME[self._finished_at.month]
        start_date = self._started_at.day
        finish_date = self._finished_at.day
        if self._started_at.month == self._finished_at.month:
            return f"{start_date} - {finish_date} {finish_month}"
        start_month = MONTH2NAME[self._started_at.month]
        return f"{start_date} {start_month} - {finish_date} {finish_month}"

    def generate_certificate(self, name: str) -> Path:
        image = create_certificate(
            template=self._template_path,
            name=name,
            date_text=self._get_date_text(),
            year_text=self._get_year_text(),
        )
        file_name = (self._working_dir / name).with_suffix(".jpeg")
        image.save(file_name)
        return Path(file_name)


class SpeechCertGen(BaseCertificateGenerator):
    template: str = "template_speech.jpeg"


class GrammarCertGen(BaseCertificateGenerator):
    template: str = "template_grammar.jpeg"


class PhraseCertGen(BaseCertificateGenerator):
    template: str = "template_phrase.jpeg"


class TextCertificateGenerator(BaseCertificateGenerator):
    template = "__no_template__"

    def generate_certificate(self, name: str) -> Path:
        file_name = self._working_dir / name
        with open(file_name, "wb") as fd:
            fd.write(f"template: {self.template}\n".encode())
            fd.write(f"name: {name}\n".encode())
            fd.write(f"date: {self._get_date_text()}\n".encode())
            fd.write(f"year: {self._get_year_text()}\n".encode())
            fd.flush()
        return Path(file_name)


def cert_gen_factory(title: WebinarTitle) -> type[BaseCertificateGenerator]:
    title_to_class = {
        WebinarTitle.SPEECH: SpeechCertGen,
        WebinarTitle.TEST: TextCertificateGenerator,
        WebinarTitle.GRAMMAR: GrammarCertGen,
        WebinarTitle.PHRASE: PhraseCertGen,
    }
    return title_to_class[title]
