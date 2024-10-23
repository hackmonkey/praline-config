from dataclasses import Field, field, dataclass, fields
from typing import Any

from config import Configuration, config_from_dict

from praline.config import load_primitive, get_field_factory, load_list, load_dict, merge_configs


def test_load_primitive():
    x: int = 1
    y: int

    y = load_primitive(int, "1")
    assert x == y
    assert type(x) == type(y)


@dataclass
class FieldTestSubject:
    int_field: int = None
    factory_field: Any = field(default_factory=str)
    no_type_field = None


def test_get_field_factory():
    for f in fields(FieldTestSubject):
        name = f.name

        match name:
            case 'int_field':
                assert get_field_factory(f) == int, "Failed test based on field type annotation."
            case 'factory_field':
                assert get_field_factory(f) == str, "Failed test based on field default factory."
            case 'no_type_field':
                assert get_field_factory(f) is None, "Failed test for missing type annotation."


def test_load_list_str():
    string_list: list[str] = ["alpha", "bravo", "charlie"]
    loaded_list: list[str] = load_list(list[str], string_list)
    assert loaded_list == string_list


def test_load_list_int():
    int_str_list: list[str] = ["1", "2", "3"]
    loaded_list: list[int] = load_list(list[int], int_str_list)
    assert loaded_list == [1, 2, 3]


def test_load_dict():
    source_dict: dict[str, str] = {
        "one": "1",
        "two": "2",
        "three": "3",
    }
    loaded_dict: dict[str, int] = load_dict(dict[str, int], source_dict)
    assert loaded_dict == {
        "one": 1,
        "two": 2,
        "three": 3,
    }


def test_merge_configs():
    first: Configuration = config_from_dict(
        {
            "hello": "world"
        }
    )
    second: Configuration = config_from_dict(
        {
            "foo": "bar"
        }
    )
    merged_config: Configuration = merge_configs([first, second])
    assert merged_config.hello == "world"
    assert merged_config.foo == "bar"


def test_merge_no_configs():
    for config_source in [[], None]:
        merged_config: Configuration = merge_configs(config_source)
        assert issubclass(type(merged_config), Configuration)
        assert len(merged_config.keys()) == 0
