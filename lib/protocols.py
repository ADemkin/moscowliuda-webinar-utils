# pylint: disable=no-self-use,unused-argument,too-few-public-methods
from typing import Any
from typing import Protocol

RowT = list[str]
RowsT = list[RowT]


class ProtoCell(Protocol):
    def value(self) -> str | None:
        ...


class ProtoSheet(Protocol):
    @property
    def title(self) -> str:
        ...

    def row_values(self, row: int) -> RowT:
        ...

    def cell(self, row: int, col: int) -> ProtoCell:
        ...

    def update_cell(self, row: int, col: int, value: str) -> dict[str, Any]:
        ...

    def append_row(self, row: RowT) -> None:
        ...

    def append_rows(self, rows: RowsT) -> None:
        ...

    def clear(self) -> None:
        ...

    def get_all_values(self) -> RowsT:
        ...


class ProtoDocument(Protocol):
    def worksheet(self, sheet: str) -> ProtoSheet:
        ...

    def worksheets(self) -> list[ProtoSheet]:
        ...

    @property
    def title(self) -> str:
        ...

    def update_title(self, title: str) -> None:
        ...

    def add_worksheet(
        self,
        title: str,
        rows: int = 100,
        cols: int = 100,
    ) -> ProtoSheet:
        ...

    def del_worksheet(self, sheet: ProtoSheet) -> None:
        ...
