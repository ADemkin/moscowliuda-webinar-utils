from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import sys

from loguru import logger
from PIL import Image  # type: ignore
from PIL import ImageDraw
from PIL import ImageFont


TEMPLATE = Path("template_without_date.jpeg")
OUTDIR = Path(".") / "certificates"

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
        date: str,
        year: str,
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
            text=date,
            anchor="ma",  # middle & top edge is anchor point
            fill=BLACK,
        )
        # fill webinar year
        ImageDraw.Draw(image).multiline_text(
            xy=get_year_position(image),
            font=get_font(DATE_FONT_SIZE),
            text=year,
            anchor="ma",  # middle & top edge is anchor point
            fill=BLACK,
        )
        return image


class Certificate:
    def __init__(
            self,
            template: Path,
            path: Path,
            name: str,
            date: str,
            year: str,
    ) -> None:
        self.template: Path = template
        self.path: Path = path
        self.name: str = name
        self.date: str = date
        self.year: str = year
        self._image: Image = None

    @classmethod
    def create(
            cls,
            template: Path,
            certs_dir: Path,
            name: str,
            date: str,
            year: int,
    ) -> 'Certificate':
        if not template.exists():
            raise RuntimeError(f"{str(template)} no exists")
        return cls(
            template=template,
            path=(certs_dir / name).with_suffix(".jpeg"),
            name=name,
            date=date,
            year=f"{year} г.",
        )

    def exists(self) -> bool:
        return self.path.exists() and self.path.is_file()

    @property
    def image(self) -> Image:
        if self._image is None:
            self._image = create_certificate(
                template=self.template,
                name=self.name,
                date=self.date,
                year=self.year,
            )
        return self._image

    def create_file(self) -> None:
        if not self.exists():
            logger.info(f"{self.path} taken")
            self.image.save(str(self.path))
            logger.info(f"{self.path} done")


def main() -> None:
    if not TEMPLATE.exists():
        logger.error(f"{str(TEMPLATE)!r} not found.")
        sys.exit(1)
    OUTDIR.mkdir(exist_ok=True)
    names = ["Пупкину Весилию Андреевичу"]
    date = "40-41 феврабля"
    year = 9999
    webinar_dir = OUTDIR / f"{date} - {year}"
    webinar_dir.mkdir(exist_ok=True)
    for name in names:
        save_to = (webinar_dir / "name").with_suffix(".jpeg")
        cert = Certificate.create(
            template=TEMPLATE,
            certs_dir=webinar_dir,
            name=name,
            date=date,
            year=year,
        )
        cert.create_file()
        assert cert.exists()
        assert cert.path == save_to, (cert.path, save_to)


if __name__ == "__main__":
    main()
