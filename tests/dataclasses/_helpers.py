"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
from typing import Any

from validataclass.dataclasses import Default
from validataclass.validators import T_Dataclass


# Test helpers for dataclass tests

def assert_field_default(field: dataclasses.Field[Any], default_value: Any) -> None:
    """
    Asserts that a given (vali-)dataclass field has a specified default value.
    """
    # Check that the field has a regular dataclass default VALUE or default FACTORY, but not both
    assert field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING
    assert field.default is dataclasses.MISSING or field.default_factory is dataclasses.MISSING

    # Check regular dataclass default
    if field.default_factory is not dataclasses.MISSING:
        assert field.default_factory() == default_value
    else:
        assert field.default == default_value

    # Check defaults in dataclass metadata
    metadata_default = field.metadata.get('validator_default')
    assert isinstance(metadata_default, Default)
    assert metadata_default.get_value() == default_value


def assert_field_no_default(field: dataclasses.Field[Any]) -> None:
    """
    Asserts that a given (vali-)dataclass field has no default value.
    """
    # Check regular dataclass defaults
    assert field.default is dataclasses.MISSING
    assert field.default_factory is dataclasses.MISSING

    # Check defaults in dataclass metadata
    assert 'validator_default' not in field.metadata


def get_dataclass_fields(cls: type[T_Dataclass]) -> dict[str, dataclasses.Field[Any]]:
    """
    Returns a dictionary containing all fields of a given dataclass.
    """
    # Make sure the class is really a dataclass
    assert dataclasses.is_dataclass(cls) and isinstance(cls, type)

    # Get fields and return them as a dictionary
    fields_tuple = dataclasses.fields(cls)
    return {field.name: field for field in fields_tuple}
