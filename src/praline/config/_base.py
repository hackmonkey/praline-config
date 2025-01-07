from dataclasses import MISSING, Field, dataclass, fields, is_dataclass
from pathlib import Path
from typing import (Any, Iterable, Optional, Self, Type, TypeVar, Union,
                    get_args, get_origin)

from config import Configuration, ConfigurationSet
from config import config as config_magic
from config import config_from_dict
from dotenv import load_dotenv

from praline.config.env import EnvValue, SecureEnvValue
from praline.config.helpers import if_any
from praline.config.logging import debug, trace, warning


def get_field_factory(f: Field):
    r"""
    Interrogates a Field to determine the function, method, or type needed to
    instantiate it.
    """
    default_factory = f.default_factory
    field_type = f.type
    factory = default_factory if default_factory not in (MISSING, None) else field_type

    if factory is None:
        warning("Could not determine a factory type. Class fields require type annotation or default_factory.")
        return None

    return factory


def load_element(factory, value) -> Any:
    r"""
    Switchboard that inspects the factory type to determine how to handle it.
    Subsequently instantiates the value based on the type of factory. This does
    not attempt to validate `value`.
    """
    _value = None
    if is_dataclass(factory):
        trace(f"{factory} is a dataclass.")
        _value = load_dataclass(factory, value)
    elif get_origin(factory) is dict:
        trace(f"{factory} is a dict.")
        _value = load_dict(factory, value)
    elif get_origin(factory) is list:
        trace(f"{factory} is a list.")
        _value = load_list(factory, value)
    else:
        try:
            trace(f"{factory} is a primitive or callable.")
            if isinstance(value, (Configuration, dict, list)):
                # If factory isn't a type we know how to handle,
                #  assume that a dict/Configuration means we should
                #  try loading it as a kwargs dict.
                trace(f"Trying load_complex for {factory}.")
                _value = load_complex(factory, value)
            if _value is None:
                # last resort attempt to instantiate the field
                trace(f"Trying last-resort, load_primitive for {factory}.")
                _value = load_primitive(factory, value)
        except Exception as ex:
            warning(f"Could not load value for: {factory} | {ex}")

    return _value


def load_complex(factory: callable, value: Configuration|dict) -> Any:
    r"""
    Best-effort attempt to load a non-dataclass object.
    """
    result = None
    try:
        parameters: Optional[dict] = None
        if isinstance(value, Configuration):
            parameters = value.as_dict()
        elif isinstance(value, dict):
            parameters = value
        result = factory(**parameters)
    except Exception as ex:
        warning(f"Could not load value for: {factory} | {ex}")
    return result


def load_primitive(factory: type, value: Any) -> Any:
    return factory(value)


_ET = TypeVar("_ET", bound=type)


@if_any
def load_dict(element_type: _ET, value: dict[str, Any]) -> dict[str, _ET]:
    r"""
    Instantiates each element of a dict based on the generic type specified for
    the field.
    """
    element_factory = get_args(element_type)[1]
    result: dict = dict()
    for key, item in value.items():
        element = load_element(element_factory, item)
        result[key] = element
    return result


def load_list(element_type: _ET, value: list[Any]) -> list[Any]:
    r"""
    Instantiates each element of a list based on the generic type specified for
    the field.
    """
    element_factory = get_args(element_type)[0]
    result: list = list()
    for item in value:
        element = load_element(element_factory, item)
        result.append(element)
    return result


_DC = TypeVar("_DC", bound=dataclass)


def load_dataclass(dc: Type[_DC], config: Configuration) -> _DC:
    r"""
    Inspects the fields of a dataclass and attempts to instantiate it from the
    Configuration object passed in.

    Walk the list of fields in `dc` and prepare a properties dict to call the
    constructor.
    """
    if config is None:
        debug("config is None")
        return None
    trace(f"dc is type: {dc}")

    properties = dict()
    for f in fields(dc):
        element: Any = None
        try:
            value: Any = config[f.name]
            element = load_element(get_field_factory(f), value)
        except KeyError:
            trace(f"{f.name} does not have a value.")

        properties[f.name] = element

    trace(f"Instantiating dataclass with properties: {properties}")
    result = dc(**properties)
    return result


AppConfigurationType = Union[Configuration, Path, dict, str]
AppConfigurationSource: Type = Union[
    Iterable[AppConfigurationType],
    AppConfigurationType,
]


def merge_configs(
        config_source: AppConfigurationSource,
) -> Configuration:
    r"""
    Detect if we have an iterable or a simple item.
    If Iterable, walk all items and turn them into a ConfigurationSet.
    """
    if config_source is None:
        return Configuration({})

    _configs_clean: list[Configuration] = list()
    match config_source:
        case cs if isinstance(cs, Configuration):
            trace("config_source is a Configuration.")
            _configs_clean.append(cs)
        case cs if isinstance(cs, dict):
            trace("config_source is a dict.")
            _configs_clean.append(config_from_dict(cs))
        case cs if isinstance(cs, str) | isinstance(cs, Path):
            trace("config_source is a Path or str.")
            _configs_clean.append(config_magic(str(cs)))
        case cs if isinstance(cs, Iterable):
            trace("config_source is an Iterable.")
            for item in cs:
                subconfig = merge_configs(item)
                if subconfig:
                    _configs_clean.append(subconfig)
                else:
                    trace("subconfig is empty.")
        case _:
            warning(f"Unknown config type: {type(config_source)}.")

    if len(_configs_clean) == 0:
        return Configuration({})

    return ConfigurationSet(*_configs_clean)


@dataclass
class EnvConfig:
    r"""
    Values mapped in from the environment.
    """
    env: dict[str, EnvValue.for_var] = None
    secure_env: dict[str, SecureEnvValue.for_var] = None


class AppConfigCore:
    @classmethod
    def load(
            cls,
            dotenv: Iterable[str | Path] = None,
            config: AppConfigurationSource | None = None,
            overrides: dict[str, Any] = None,
    ) -> Self:
        r"""
        Convenience method to ergonomically instantiate an AppConfig class or
        subclass.

        This handles loading .env files, merging various Configuration sources,
        applies "overrides", such as may be sourced from command line
        parameters.
        """
        if dotenv:
            for env_source in dotenv:
                if isinstance(env_source, Path):
                    with env_source.open("r") as istream:
                        load_dotenv(stream=istream)
                else:
                    load_dotenv(dotenv_path=env_source)

        if (
            config is None
            or (
                issubclass(type(config), Iterable)
                and len(config) == 0
            )
        ) and (
            overrides is None
            or len(overrides) == 0
        ):
            trace("No config was provided; calling empty constructor.")
            return cls()

        _config: Configuration = merge_configs(
            [
                config_from_dict(overrides or {}),
                config
            ]
        )

        instance: Self = load_dataclass(cls, config=_config)
        return instance


@dataclass
class AppConfigBase(AppConfigCore, EnvConfig):
    r"""
    Convenience class to use as a base for AppConfig subclasses.
    """
    ...
