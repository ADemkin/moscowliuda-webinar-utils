from dataclasses import field
from functools import partial
from os import environ
from typing import Callable


class EnvironmentVariableNotSetError(Exception):
    def __init__(self, variable: str) -> None:
        super().__init__(f"Environment variable {variable!r} is not set")


def get_env_variable[T](
    *,
    cast: Callable[[str], T],
    var_name: str,
    default: T | None = None,
) -> T:
    if (value := environ.get(var_name)) is not None:
        return cast(value)
    if default is not None:
        return default
    raise EnvironmentVariableNotSetError(var_name)


def env_str_field(var_name: str, default: str | None = None) -> str:
    return field(
        default_factory=partial(
            get_env_variable,
            cast=str,
            var_name=var_name,
            default=default,
        ),
    )


def env_str_tuple_field(var_name: str) -> tuple[str, ...]:
    def split_to_str(text: str) -> tuple[str, ...]:
        return tuple(str(e) for e in text.split(","))

    return field(
        default_factory=partial(
            get_env_variable,
            cast=split_to_str,
            var_name=var_name,
        ),
    )
