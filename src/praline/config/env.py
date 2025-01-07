import os
from typing import Self

from praline.config.model import SecureValue, WrappedValue


class EnvValue(WrappedValue):
    r"""
    Convenience class to bind values from the environment into
    a simple WrappedValue instance.
    """
    @classmethod
    def for_var(cls, name: str) -> Self:
        return cls(value=os.environ.get(name))


class SecureEnvValue(EnvValue, SecureValue):
    r"""
    Simple confluence of an EnvValue that needs to be wrapped securely for cases
    such as passwords that are "passed" to a program via environment variables.
    """
    ...
