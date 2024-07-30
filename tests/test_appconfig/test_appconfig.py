import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import pytest
from config import config_from_yaml

from praline.config import AppConfigBase
from praline.helpers import if_any


@dataclass
class UserObject:
    name: str = None
    age: int = None


@if_any
def datetime_factory(val: str | datetime) -> datetime:
    if isinstance(val, datetime):
        return val
    result = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
    return result


@dataclass
class AppConfig(AppConfigBase):
    str_field: str = None
    int_field: int = None
    float_field: float = None
    float_alternate: float = None
    decimal_field: Decimal = None
    datetime_field: datetime = field(default_factory=datetime_factory)
    datetime_str_field: datetime = field(default_factory=datetime_factory)
    list_field: list = None
    dict_field: dict = None
    uuid_field: UUID = None
    user_object: UserObject = None
    user_list: list[UserObject] = None
    user_map: dict[str, UserObject] = None


@pytest.fixture
def config_yaml() -> str:
    return textwrap.dedent(
        r"""
            gibberish: Nonsense.
            str_field: "Hello, world!"
            int_field: 999
            float_field: 3.14
            float_alternate: "3.14"
            decimal_field: "3.14"
            datetime_field: 2020-03-03T12:34:56
            datetime_str_field: "2020-03-03T12:34:56"
            list_field: [1, 2, 3]
            dict_field: {"key": "value"}
            uuid_field: "6794f37e-22e7-11ef-b440-971e96ae0c81"
            user_object: {"name": "John", "age": 32}
            user_list: 
                - name: "Alice"
                  age: 20
                - name: "Bob"
                  age: 40
            user_map:
                president: {"name": "Alice", "age": 32}
                cfo:
                  name: Bob
                  age: 42
        """
    )


def test_app_config(config_yaml):
    configs = [config_from_yaml(config_yaml)]
    app_config: AppConfig = AppConfig.load(
        config=configs
    )
    assert app_config.str_field == "Hello, world!"
    assert app_config.int_field == 999
    assert app_config.float_field == 3.14
    assert app_config.float_field == 3.14
    assert app_config.decimal_field == Decimal("3.14")
    assert app_config.datetime_field == datetime(2020, 3, 3, 12, 34, 56)
    assert app_config.datetime_str_field == datetime(2020, 3, 3, 12, 34, 56)
    assert app_config.list_field == [1, 2, 3]
    assert app_config.dict_field == {"key": "value"}
    assert app_config.uuid_field == UUID("6794f37e-22e7-11ef-b440-971e96ae0c81")

    assert UserObject(name="John", age=32) == app_config.user_object

    assert len(app_config.user_list) == 2
    assert UserObject(name="Alice", age=20) in app_config.user_list

    assert len(app_config.user_map) == 2
    assert UserObject(name="Bob", age=42) == app_config.user_map["cfo"]
    ...


def test_empty_config():
    app_config = AppConfig.load(
        config=None,
    )
    assert isinstance(app_config, AppConfig)
    ...
