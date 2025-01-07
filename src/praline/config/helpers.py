import csv
from pathlib import Path
from typing import Any, Callable, TypeVar

_T = TypeVar("_T")


def nullif(value: _T, test: _T) -> _T | None:
    r"""
    We aren't confirming the types, so this might surprise a caller sometimes.
    """
    # todo: Consider comparing types instead of letting Python coerce values
    #   automatically.
    if value == test:
        return None
    return value


def csv_to_nested_dict(csv_file: Path, key_fields: list[str], key_delimiter: str = None) -> dict[str, dict[str, str]]:
    r"""
    For the csv file passed in, generate a dictionary that is keyed by the column identified by key_field.
    The value for each entry in the dictionary will be a dictionary with the complete record for the given line.
    """

    key_delimiter_ = "," if key_delimiter is None else key_delimiter
    def row_key(current_row: dict[str, Any]) -> str:
        key_values: list[str] = []
        for key_field in key_fields:
            key_values.append(current_row[key_field])
        return key_delimiter_.join(key_values)

    nested_dict = {}
    with csv_file.open('r', newline='') as file:
        reader = csv.DictReader(file)
        # field_names = reader.fieldnames
        for row in reader:
            # row_dict: dict[str, Any] = zip(field_names, row)
            parent_key = row_key(current_row=row)
            nested_dict[parent_key] = row

    return nested_dict


def call_if_any(fn: Callable, *args, **kwargs):
    if len(args) + len(kwargs) == 0:
        return None
    elif len(args) > 0:
        for a in args:
            if a is not None:
                return fn(*args, **kwargs)
    elif len(kwargs) > 0:
        for k, v in kwargs.items():
            if v is not None:
                return fn(*args, **kwargs)
    return None


def if_any(fn: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return call_if_any(fn, *args, **kwargs)
    return wrapper


