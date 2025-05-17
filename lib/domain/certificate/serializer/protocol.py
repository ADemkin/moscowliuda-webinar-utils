from typing import BinaryIO
from typing import Protocol


class Serializable(Protocol):
    def serialize(
        self,
        buffer: BinaryIO,
        title: str,
        name: str,
        date_text: str,
    ) -> None: ...
