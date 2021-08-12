"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import dataclasses
from typing import Optional

from wtfjson.validators import IntegerValidator, StringValidator, Noneable
from wtfjson.helpers import validator_dataclass, validator_field


class DataclassHelperTest:
    # Tests for validator_field()

    @staticmethod
    def test_validator_fields_in_dataclass():
        """ Create a dataclass with validator_field() and check that the fields are created correctly. """

        @dataclasses.dataclass
        class UnitTestDataclass:
            foo: int = validator_field(IntegerValidator())
            bar: int = validator_field(IntegerValidator(), default=1)
            baz: int = validator_field(IntegerValidator(), default=2, metadata={'unittest': 123, 'validator': 'this gets overwritten'})

        # Get fields from dataclass
        fields = dataclasses.fields(UnitTestDataclass)

        # Check names, types and default values of all fields
        assert [f.name for f in fields] == ['foo', 'bar', 'baz']
        assert all([f.type is int for f in fields])
        assert [f.default for f in fields] == [dataclasses.MISSING, 1, 2]

        # Check that all fields have an IntegerValidator object as validator
        assert all([type(f.metadata.get('validator')) is IntegerValidator for f in fields])

        # Check that addition metadata is preserved if specified (only for field 'baz')
        assert fields[2].metadata.get('unittest') == 123

    # Tests for @validator_dataclass decorator

    @staticmethod
    def test_validator_dataclass_without_kwargs():
        """ Create a dataclass using @validator_dataclass and check that all fields with metadata are created correctly. """

        @validator_dataclass
        class UnitTestValidatorDataclass:
            foo: int = IntegerValidator()
            bar: Optional[int] = Noneable(IntegerValidator())
            baz: Optional[str] = validator_field(StringValidator(), default=None)

        # Check that validator_dataclass actually created a dataclass (i.e. used @dataclass on the class)
        assert dataclasses.is_dataclass(UnitTestValidatorDataclass)

        # Get fields from dataclass
        # Note: Pycharm complains again about dataclasses not being dataclasses...
        fields = dataclasses.fields(UnitTestValidatorDataclass)  # noqa

        # Check names, types and default values of all fields
        assert [f.name for f in fields] == ['foo', 'bar', 'baz']
        assert [f.type for f in fields] == [int, Optional[int], Optional[str]]
        assert [f.default for f in fields] == [dataclasses.MISSING, dataclasses.MISSING, None]

        # Check that fields have correct validators
        assert [type(f.metadata.get('validator')) for f in fields] == [IntegerValidator, Noneable, StringValidator]

    @staticmethod
    def test_validator_dataclass_with_kwargs():
        """ Create a dataclass using @validator_dataclass(...) with arguments and check that they are passed to @dataclass(). """

        # Create two dataclasses, one without any arguments and one with unsafe_hash=True. The first won't have a __hash__ function,
        # but the latter will have one. We can use this to check that the argument was really passed to @dataclass.

        @validator_dataclass()
        class FooDataclass:
            foo: int = IntegerValidator()

        @validator_dataclass(unsafe_hash=True)
        class BarDataclass:
            foo: int = IntegerValidator()

        # Check that validator_dataclass actually created a dataclass (i.e. used @dataclass on the class)
        assert dataclasses.is_dataclass(FooDataclass)
        assert dataclasses.is_dataclass(BarDataclass)

        # Check if __hash__ exists
        assert FooDataclass.__hash__ is None
        assert BarDataclass.__hash__ is not None
