from typing import IO
from typing import Protocol


class Serializable(Protocol):
    def serialize(
        self,
        buffer: IO[bytes],
        title: str,
        name: str,
        date_text: str,
    ) -> None: ...
