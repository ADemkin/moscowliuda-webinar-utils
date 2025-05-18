from typing import BinaryIO


class CertificateTextSerializer:
    def serialize(
        self,
        buffer: BinaryIO,
        title: str,
        name: str,
        date_text: str,
    ) -> None:
        buffer.write(f"{title} {name} {date_text}".encode())
