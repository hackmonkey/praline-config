import importlib
from dataclasses import dataclass
from functools import cache
from typing import Any, ClassVar, Callable

from praline.model import HasReify, HasInit, SingletonBase
from praline.logging import debug, warning


@dataclass
class Registrar(SingletonBase):
    r"""
    Register names with values. Pretty much just a dictionary
    but this is derived from the SingletonBase so it does not
    need to be passed around to be used. Can be used to inject
    values throughout an application or provide a global lookup
    mechanism.
    """
    _items: ClassVar[dict[str, Any]] = {}

    @classmethod
    def register(cls, key: str, item: Any):
        cls._items[key] = item

    @classmethod
    def get(cls, key: str) -> Any:
        return cls._items[key]


@dataclass
class AliasRegistrar(Registrar):
    r"""
    Specialized registrar intended to map between strings, such
    as to provide friendly names or abbreviations to longer
    or dynamically generated values. For unregistered strings,
    just return the input unmodified.
    """
    @classmethod
    def get(cls, key: str) -> str:
        try:
            return cls._items[key]
        except KeyError:
            return key


@cache
def get_callable(name: str) -> Callable:
    r"""
    ***Warning: Do Not use this with untrusted inputs!***

    Attempt to import and lookup a named callable.
    """
    module = importlib.import_module(".".join(name.split(".")[:-1]))
    factory = getattr(module, name.split(".")[-1])
    return factory


@dataclass
class ReifiableConfig(HasReify):
    r"""
    ***Warning: Do Not use this with untrusted inputs!***

    ReifiableConfig is intended to be used to inject object instances
    via configuration data. It will use a named callable, type, or class
    to instantiate the object based on the provided arguments.
    """
    factory: str = None
    args: tuple = None
    kwargs: dict[str, Any] = None
    _factory: Callable | type | None = None

    def _build_factory(self):
        r"""
        ***Warning: Do Not use this with untrusted inputs!***

        Resolved aliased factory names as needed and return the resulting
        factory.
        """
        self._factory = None
        try:
            self._factory = get_callable(AliasRegistrar.get(self.factory))
        except Exception as ex:
            warning(f"Could not resolve factory name: {self.factory}")
            debug(f"FactoryConfig.init() exception: {ex}")

    def reify(self):
        r"""
        Implement HasReify based on the possibly aliased named factory.
        """
        if self._factory is None:
            self._build_factory()
        if self._factory is not None:
            return self._factory(*self.args, **self.kwargs)
        warning("Failed to reify object.")
        return None


@dataclass
class ObjectRegistrar(Registrar):
    r"""
    Specialized Registrar to map friendly or well-defined names to
    objects instantiated at run-time, usually based on configuration
    data. Enables configuration information to reference objects
    that won't exist until run-time.
    """
    ...


@dataclass
class RegisteredObjectConfig(HasInit, ReifiableConfig):
    r"""
    Dataclass to use in AppConfig to create an object that can be
    referenced by name in other configuration entries.
    """
    name: str = None

    def init(self):
        super().init()
        instance = self.reify()
        ObjectRegistrar.register(self.name, instance)
