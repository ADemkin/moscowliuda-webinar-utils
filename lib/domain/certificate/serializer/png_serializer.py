from dataclasses import dataclass
from dataclasses import field
from io import BytesIO
from pathlib import Path

from PIL.Image import Image
from PIL.Image import open as _open_image
from PIL.ImageDraw import Draw
from PIL.ImageFont import FreeTypeFont
from PIL.ImageFont import truetype

from .paths import get_png_template_path

BLACK = (0, 0, 0)


@dataclass(frozen=True, slots=True)
class CertificatePNGSerializer:
    template: Path = field(default_factory=get_png_template_path)

    @staticmethod
    def _get_font(size: int) -> FreeTypeFont:
        return truetype(font="Arial", size=size)

    def _get_small_font(self) -> FreeTypeFont:
        return self._get_font(size=82)

    def _get_large_font(self) -> FreeTypeFont:
        return self._get_font(size=137)

    def _get_name_font(
        self,
        image: Image,
        name: str,
        min_size: int = 100,
        max_size: int = 150,
        max_rel_text_width: float = 0.81,
    ) -> FreeTypeFont:
        image_width, _ = image.size
        max_text_width = image_width * max_rel_text_width
        for font_size in range(min_size, max_size):
            if self._get_font(font_size).getlength(name) > max_text_width:
                break
        return self._get_font(font_size)

    def get_image(self, title: str, name: str, date_text: str) -> Image:
        image = _open_image(self.template)
        center = image.width // 2
        small_font = self._get_small_font()
        large_font = self._get_large_font()
        name_font = self._get_name_font(image, name)
        spacing = 18
        draw = Draw(image)
        draw.text(
            xy=(center, 1650),
            text="подтверждает, что",
            font=small_font,
            fill=BLACK,
            anchor="ms",
        )
        draw.text(
            xy=(center, 1900),
            text=name,
            font=name_font,
            fill=BLACK,
            anchor="ms",
        )
        draw.multiline_text(
            xy=(center, 2160),
            text="прошла практическую\nи теоретическую части вебинара",
            align="center",
            font=small_font,
            spacing=spacing,
            anchor="mm",
            fill=BLACK,
        )
        draw.multiline_text(
            xy=(center, 2540),
            text=f"«{title}»",
            align="center",
            font=large_font,
            spacing=spacing,
            anchor="mm",
            fill=BLACK,
        )
        draw.multiline_text(
            xy=(270, 3100),
            text=date_text,
            align="left",
            font=small_font,
            anchor="lm",
            spacing=spacing,
            fill=BLACK,
        )
        return image

    def serialize(
        self,
        buffer: BytesIO,
        title: str,
        name: str,
        date_text: str,
    ) -> None:
        image = self.get_image(title, name, date_text)
        image.save(buffer, format="png", mode="rgb")
