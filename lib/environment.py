from dataclasses import field
from functools import partial
from os import environ
from typing import Callable
from typing import TypeVar

T = TypeVar("T")


class EnvironmentVariableNotSetError(Exception):
    ...


def get_env_variable(
    factory: Callable[[str], T],
    var_name: str,
    default: str = None,
) -> T:
    if (value := environ.get(var_name, default)) is not None:
        return factory(value)
    raise EnvironmentVariableNotSetError(
        f"Environment variable {var_name!r} is not set"
    )


get_env_str_var = partial(get_env_variable, factory=str)


def env_str_field(var_name: str, default: str = None) -> str:
    return field(
        default_factory=partial(
            get_env_str_var,
            var_name=var_name,
            default=default,
        ),
    )
