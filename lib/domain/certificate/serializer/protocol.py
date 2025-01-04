from io import BytesIO
from typing import Protocol


class Serializable(Protocol):
    def serialize(
        self,
        buffer: BytesIO,
        title: str,
        name: str,
        date_text: str,
    ) -> None: ...
