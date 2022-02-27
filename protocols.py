from typing_extensions import Protocol


RowT = list[str | None]
RowsT = list[RowT]


class ProtoCell(Protocol):
    def value(self) -> str | None:
        ...


class ProtoSheet(Protocol):
    def row_values(self, row: int) -> list[str | None]:
        ...

    def cell(self, row: int, col: int) -> ProtoCell:
        ...

    def update_cell(self, row: int, col: int, value: str) -> dict:
        ...

    def append_row(self, row: list[str | None]) -> None:
        ...

    def append_rows(self, rows: list[list[str | None]]) -> None:
        ...

    def clear(self) -> None:
        ...
