"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import dataclasses
from typing import Optional, Any
import pytest

from wtfjson.exceptions import DataclassValidatorFieldException
from wtfjson.helpers import validator_dataclass, validator_field, Default, NoDefault
from wtfjson.validators import IntegerValidator, StringValidator, Noneable


# Test helpers
def assert_field_default(field: dataclasses.Field, default_value: Any, default_type: type = Default):
    metadata_default = field.metadata.get('validator_default')
    assert type(metadata_default) is default_type
    assert metadata_default.value == default_value


class ValidatorFieldTest:
    # Tests for validator_field()

    @staticmethod
    def test_validator_fields_in_dataclass():
        """ Create a dataclass with validator_field() and check that the fields are created correctly. """

        @dataclasses.dataclass
        class UnitTestDataclass:
            foo: int = validator_field(IntegerValidator())
            bar: int = validator_field(IntegerValidator(), default=Default(1))
            baz: int = validator_field(IntegerValidator(), default=42, metadata={'unittest': 123, 'validator': 'this gets overwritten'})

        # Get fields from dataclass
        fields = dataclasses.fields(UnitTestDataclass)

        # Check names and types of all fields
        assert [f.name for f in fields] == ['foo', 'bar', 'baz']
        assert all(f.type is int for f in fields)

        # Check that all fields have an IntegerValidator object as validator
        assert all(type(f.metadata.get('validator')) is IntegerValidator for f in fields)

        # Check that dataclass fields do *not* have regular default values
        assert all(f.default is dataclasses.MISSING for f in fields)

        # Check metadata for Default objects (first field should not have one, others should)
        assert 'validator_default' not in fields[0].metadata
        assert_field_default(fields[1], default_value=1)
        assert_field_default(fields[2], default_value=42)

        # Check that addition metadata is preserved if specified (only for field 'baz')
        assert fields[2].metadata.get('unittest') == 123

    @staticmethod
    def test_validator_field_with_init_kwarg_raises_exception():
        """ Test that validator_field() does not allow the 'init' keyword argument. """
        with pytest.raises(ValueError) as exception_info:
            validator_field(IntegerValidator(), init=False)

        assert str(exception_info.value) == 'Keyword argument "init" is not allowed in validator field.'

    @staticmethod
    def test_validator_field_with_default_factory_kwarg_raises_exception():
        """ Test that validator_field() does not allow the 'default_factory' keyword argument. """
        with pytest.raises(ValueError) as exception_info:
            validator_field(IntegerValidator(), default_factory=list)

        assert str(exception_info.value) == \
               'Keyword argument "default_factory" is not allowed in validator field (use default=DefaultFactory(...) instead).'


class ValidatorDataclassTest:
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

        # Check names and types of all fields
        assert [f.name for f in fields] == ['foo', 'bar', 'baz']
        assert [f.type for f in fields] == [int, Optional[int], Optional[str]]

        # Check that dataclass fields have NOT set regular default values
        assert all(f.default is dataclasses.MISSING for f in fields)

        # Check for defaults in metadata (only the last one should have a default value, which is None)
        assert 'validator_default' not in fields[0].metadata
        assert 'validator_default' not in fields[1].metadata
        assert_field_default(fields[2], default_value=None)

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

    @staticmethod
    def test_validator_dataclass_with_tuples():
        """ Create a dataclass using @validator_dataclass with tuple syntax for setting Defaults. """

        @validator_dataclass
        class UnitTestValidatorDataclass:
            foo: int = IntegerValidator(), NoDefault
            bar: int = IntegerValidator(), Default(42)
            baz: Optional[int] = IntegerValidator(), Default(None)

        # Get fields from dataclass
        fields = dataclasses.fields(UnitTestValidatorDataclass)  # noqa

        # Check names and types of all fields
        assert [f.name for f in fields] == ['foo', 'bar', 'baz']
        assert [f.type for f in fields] == [int, int, Optional[int]]

        # Check that dataclass fields have NOT set regular default values
        assert all(f.default is dataclasses.MISSING for f in fields)

        # Check for defaults in metadata (only the last one should have a default value, which is None)
        assert 'validator_default' not in fields[0].metadata
        assert_field_default(fields[1], default_value=42)
        assert_field_default(fields[2], default_value=None)

        # Check that fields have correct validators
        assert all(type(f.metadata.get('validator')) is IntegerValidator for f in fields)

    @staticmethod
    def test_validator_dataclass_with_non_init_fields():
        """ Create a dataclass using @validator_dataclass with fields that have init=False. """

        @validator_dataclass
        class UnitTestValidatorDataclass:
            foo: int = IntegerValidator()
            bar: int = dataclasses.field(init=False, default=1)

        # Get fields from dataclass
        fields = dataclasses.fields(UnitTestValidatorDataclass)  # noqa

        # Check names and types of all fields
        assert [f.name for f in fields] == ['foo', 'bar']
        assert all(f.type is int for f in fields)

        # Check 'init' value
        assert fields[0].init is True
        assert fields[1].init is False

        # Check that non-init field has regular default value
        assert fields[0].default is dataclasses.MISSING
        assert fields[1].default == 1

        # Check that non-init field has no validator metadata
        assert type(fields[0].metadata.get('validator')) is IntegerValidator
        assert 'validator' not in fields[1].metadata

    @staticmethod
    def test_validator_dataclass_with_invalid_values():
        """ Test that @validator_dataclass raises exceptions when a field is not predefined (e.g. with field()) and has no Validator. """

        class InvalidDataclassA:
            foo: int

        class InvalidDataclassB:
            foo: int = 3

        class InvalidDataclassC:
            # Wrong order, first element of tuple must be validator
            foo: int = Default(5), IntegerValidator()

        for cls in [InvalidDataclassA, InvalidDataclassB, InvalidDataclassC]:
            with pytest.raises(DataclassValidatorFieldException) as exception_info:
                validator_dataclass(cls)
            assert str(exception_info.value) == 'Dataclass field "foo" must specify a Validator.'

    @staticmethod
    def test_validator_dataclass_with_invalid_tuple_length():
        """ Test that @validator_dataclass raises exceptions when a field has a tuple with invalid length. """

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            @validator_dataclass
            class InvalidDataclass:
                foo: int = IntegerValidator(), Default(5), Default(3)

        assert str(exception_info.value) == 'Dataclass field "foo": Unexpected number of arguments.'

    @staticmethod
    def test_validator_dataclass_with_invalid_tuple_arguments():
        """ Test that @validator_dataclass raises exceptions when a field has a tuple with invalid arguments. """

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            @validator_dataclass
            class InvalidDataclass:
                foo: int = IntegerValidator(), 5

        assert str(exception_info.value) == 'Dataclass field "foo": Unexpected type of argument (expected Default).'
