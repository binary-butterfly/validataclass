"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
import sys
from typing import Any, Dict, Type, TYPE_CHECKING

import pytest

from validataclass.dataclasses import Default
from validataclass.validators import T_Dataclass

# TODO: Replace type alias with dataclasses.Field[Any] when removing Python 3.9 support. (#15)
if TYPE_CHECKING:
    T_DataclassField = dataclasses.Field[Any]
else:
    T_DataclassField = dataclasses.Field


# Test helpers for dataclass tests

def assert_field_default(field: T_DataclassField, default_value: Any) -> None:
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


def assert_field_no_default(field: T_DataclassField) -> None:
    """
    Asserts that a given (vali-)dataclass field has no default value.
    """
    # Check regular dataclass defaults
    assert field.default is dataclasses.MISSING

    # Check defaults in dataclass metadata
    assert 'validator_default' not in field.metadata

    # For Python under 3.10, check that an exception raising default_factory is set
    if sys.version_info < (3, 10):
        with pytest.raises(TypeError, match="required keyword-only argument"):
            field.default_factory()
    else:
        assert field.default_factory is dataclasses.MISSING


def get_dataclass_fields(cls: Type[T_Dataclass]) -> Dict[str, T_DataclassField]:
    """
    Returns a dictionary containing all fields of a given dataclass.
    """
    # Make sure the class is really a dataclass
    assert dataclasses.is_dataclass(cls) and isinstance(cls, type)

    # Get fields and return them as a dictionary
    fields_tuple = dataclasses.fields(cls)
    return {field.name: field for field in fields_tuple}
