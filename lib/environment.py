from dataclasses import field
from functools import partial
from os import environ
from typing import Any
from typing import Callable


class EnvironmentVariableNotSetError(Exception):
    ...


def get_env_variable(
    cast: Callable,
    var_name: str,
    default: Any | None = None,
) -> str:
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
