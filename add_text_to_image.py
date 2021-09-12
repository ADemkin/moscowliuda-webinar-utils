from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import sys

from PIL import Image  # type: ignore
from PIL import ImageDraw
from PIL import ImageFont


TEMPLATE = Path("template.jpeg")
INPUTFILE = Path("список.txt")
OUTDIR = Path(".") / "out"
CLEANUP = True

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
FONT = "Helvetica"
MIN_FONT_SIZE = 20
MAX_FONT_SIZE = 35


def load_names_from_file(filename: Path) -> list[str]:
    with open(filename, "r", encoding="utf-8") as fd:
        return [line.strip() for line in fd.readlines() if line != '\n']


@lru_cache(maxsize=MAX_FONT_SIZE - MIN_FONT_SIZE)
def get_font(size: int = 10) -> ImageFont:
    return ImageFont.truetype(FONT, size=size)


def get_max_text_size(image: Image) -> tuple[float, float]:
    return MAX_TEXT_SIZE * image.size


def get_text_position(image: Image) -> tuple[float, float]:
    return TEXT_POSITION * image.size


def calculate_largest_font_size_for_text(image: Image, text: str) -> ImageFont:
    max_text_size = get_max_text_size(image)
    for font_size in range(MIN_FONT_SIZE, MAX_FONT_SIZE):
        font = get_font(size=font_size)
        if font.getsize_multiline(text) > max_text_size:
            break
    return font_size


def add_text_to_image_file(template: str, text: str, save_to: str) -> None:
    with Image.open(template) as image:
        font_size = calculate_largest_font_size_for_text(image, text)
        ImageDraw.Draw(image).multiline_text(
            xy=get_text_position(image),
            font=get_font(font_size),
            text=text,
            anchor="ma",
            fill=BLACK,
        )
        # image.show()
        image.save(save_to)
        print(f"saved to: {save_to}")


def main() -> None:
    if CLEANUP and OUTDIR.exists():
        for item in OUTDIR.iterdir():
            item.unlink()
        OUTDIR.rmdir()
        print(f"cleanup for {str(OUTDIR)!r}")
    if not OUTDIR.exists():
        OUTDIR.mkdir()
    if not TEMPLATE.exists():
        print(f"{str(TEMPLATE)!r} not found.")
        sys.exit(1)
    if not INPUTFILE.exists():
        print(f"{str(INPUTFILE)!r} not found.")
        sys.exit(1)
    names = load_names_from_file(INPUTFILE)
    for name in names:
        save_to = OUTDIR / f"{name}.jpeg"
        add_text_to_image_file(str(TEMPLATE), name, str(save_to))


if __name__ == "__main__":
    main()
