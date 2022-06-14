"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
import sys
from typing import Any

import pytest

from validataclass.dataclasses import Default


# Test helpers for dataclass tests

def assert_field_default(field: dataclasses.Field, default_value: Any):
    """
    Asserts that a given (vali-)dataclass field has a specified default value.
    """
    # Check regular dataclass defaults
    assert field.default == default_value

    # Check defaults in dataclass metadata
    metadata_default = field.metadata.get('validator_default')
    assert isinstance(metadata_default, Default)
    assert metadata_default.get_value() == default_value


def assert_field_no_default(field: dataclasses.Field):
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


def get_dataclass_fields(cls) -> dict:
    """
    Returns a dictionary containing all fields of a given dataclass.
    """
    fields_tuple = dataclasses.fields(cls)
    return {field.name: field for field in fields_tuple}
