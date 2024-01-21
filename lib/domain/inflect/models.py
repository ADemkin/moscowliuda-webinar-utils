from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Inflection:
    base: str
    datv: str
    is_confirmed: bool
