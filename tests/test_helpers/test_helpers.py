import tempfile
from pathlib import Path

import pytest

from praline.config.helpers import csv_to_nested_dict, if_any, nullif


def test_nullif():
    assert nullif("a", "a") is None
    assert nullif("a_value", "a_sentinel") == "a_value"


@if_any
def echo(istring: str) -> str:
    if istring is None:
        return "default"
    return istring


def test_if_any():
    assert echo("Hello, world!") == "Hello, world!"
    assert echo() is None
    assert echo(None) is None
    assert echo("") == ""


@pytest.fixture
def csv_file():
    temp_csv = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
    temp_csv.write("id,name,age\n1,Alice,30\n2,Bob,25\n3,Charlie,35\n")
    temp_csv.close()
    csv_path = Path(temp_csv.name)
    yield csv_path
    csv_path.unlink()


def test_csv_to_nested_dict(csv_file):
    key_fields = ['id', 'name']
    expected_output = {
        '1,Alice': {'id': '1', 'name': 'Alice', 'age': '30'},
        '2,Bob': {'id': '2', 'name': 'Bob', 'age': '25'},
        '3,Charlie': {'id': '3', 'name': 'Charlie', 'age': '35'},
    }
    result = csv_to_nested_dict(csv_file, key_fields)
    assert result == expected_output


def test_csv_to_nested_dict_delimiter(csv_file):
    key_fields = ['id', 'name']
    delimiter = "|"
    expected_output = {
        '1|Alice': {'id': '1', 'name': 'Alice', 'age': '30'},
        '2|Bob': {'id': '2', 'name': 'Bob', 'age': '25'},
        '3|Charlie': {'id': '3', 'name': 'Charlie', 'age': '35'},
    }
    result = csv_to_nested_dict(csv_file, key_fields, key_delimiter=delimiter)
    assert result == expected_output
