from dataclasses import field
from functools import partial
from os import environ
from typing import Any
from typing import Callable


class EnvironmentVariableNotSetError(Exception): ...


def get_env_variable(
    cast: Callable[[str], Any],
    var_name: str,
    default: Any | None = None,
) -> Any:
    if (value := environ.get(var_name, default)) is not None:
        return cast(value)
    raise EnvironmentVariableNotSetError(f"Environment variable {var_name!r} is not set")


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
