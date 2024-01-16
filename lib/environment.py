from dataclasses import Field
from dataclasses import field
from functools import partial
from os import environ
from typing import Callable
from typing import TypeVar

T = TypeVar("T")


class EnvironmentVeriableNotSetError(Exception):
    ...


def get_env_variable(
    factory: Callable[[str], T],
    var_name: str,
    default: str = None,
) -> T:
    if (value := environ.get(var_name, default)) is not None:
        return factory(value)
    raise EnvironmentVeriableNotSetError(
        f"Environment variable {var_name!r} is not set"
    )


get_env_str_var = partial(get_env_variable, factory=str)


def env_str_field(var_name: str, default: str = None) -> Field:
    return field(default_factory=partial(get_env_str_var, var_name, default))
