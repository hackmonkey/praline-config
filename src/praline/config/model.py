from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Self, Type

from praline.config.logging import warning


class HasReify:
    r"""
    Class mixin for config classes that can be reified into a functional
    instance. Intended to separate the config entries for things like database
    adapters and similar without having to instantiate them from a config entry
    in a separately defined function.
    """
    @classmethod
    def reify_type(cls) -> Type | None:
        r"""
        Don't require implementations to include this, but report None when
        called so a consumer can determine that it has not been overridden.
        """
        return None

    @abstractmethod
    def reify(self) -> Any: ...


class HasInit:
    r"""
    Ensure that init() gets called on regular classes and data classes and
    provide a safe super().init() to call in all subclasses. Also manage a flag
    to indicate when the object has been initialized.
    """
    _has_initialized: bool = False

    def init(self):
        self._has_initialized = True

    def __init__(self, *args, **kwargs):
        self.init()

    def __post_init__(self):
        self.init()

    def is_initialized(self) -> bool:
        return self._has_initialized


@dataclass
class SingletonBase(HasInit):
    r"""
    Each class inheriting from SingletonBase can each have up to one singleton
    instance created. Use subclasses to allow various singletons, each of
    their specific class type.

    Any subclass that overrides the HasInit.init() method *must* either explicitly
    call `cls._bind_instance(self)` or `super().init()` to ensure the singleton
    instance is properly bound to the class.
    """
    _instance: ClassVar["SingletonBase"] = None

    @classmethod
    def _bind_instance(cls, self):
        r"""
        Binds the singleton to the class/subclass.
        """
        cls._instance = self

    @classmethod
    def instance(cls) -> Self:
        r"""
        Get the instance bound to the class.
        """
        if cls._instance is None:
            warning(f"Attempt to get null instance of {cls.__name__}. Did you override `init` without super()?")
        return cls._instance

    def init(self):
        r"""
        Ensure that we always call _bind_instance when instantiating a singleton class.
        :return:
        """
        self._bind_instance(self)
        super().init()


class WrappedValue:
    r"""
    Base class for various subclasses that need special behavior when being
    coerced to a string vs. explicit value access.
    """
    def __init__(self, value: str):
        self._value: str = value

    def value(self) -> str:
        r"""
        Default implementation simply returns the value "wrapped" by the
        class.
        """
        return self._value

    def __str__(self) -> str:
        r"""
        By default, string coercion will just call string conversion on the
        wrapped value.
        """
        return str(self._value)

    def __repr__(self) -> str:
        r"""
        Return the string representation of the wrapped value.
        """
        return str(self)


class SecureValue(WrappedValue):
    r"""
    SecureValue shields the wrapped value from unintentional exposure via
    string coercion or processes that may call __repr__. Specifically intended
    to protect values from being written to application logs accidentally.
    """
    mask_str: str = "***"

    def __str__(self):
        return self.mask_str
