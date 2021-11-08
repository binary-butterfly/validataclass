"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
from typing import Optional, Any, Union
import pytest

from validataclass.exceptions import DataclassValidatorFieldException
from validataclass.helpers import validataclass, validataclass_field, Default, NoDefault, DefaultUnset, UnsetValueType
from validataclass.validators import IntegerValidator, StringValidator, Noneable


# Test helpers
def assert_field_default(field: dataclasses.Field, default_value: Any, default_type: type = Default):
    metadata_default = field.metadata.get('validator_default')
    assert type(metadata_default) is default_type
    assert metadata_default.value == default_value


class ValidataclassFieldTest:
    """ Tests for the validataclass_field() helper method. """

    @staticmethod
    def test_validataclass_fields_in_dataclass():
        """ Create a dataclass with validataclass_field() and check that the fields are created correctly. """

        @dataclasses.dataclass
        class UnitTestDataclass:
            foo: int = validataclass_field(IntegerValidator())
            bar: int = validataclass_field(IntegerValidator(), default=Default(1))
            baz: int = validataclass_field(IntegerValidator(), default=42, metadata={'unittest': 123, 'validator': 'gets overwritten'})

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
    def test_validataclass_field_with_init_kwarg_raises_exception():
        """ Test that validataclass_field() does not allow the 'init' keyword argument. """
        with pytest.raises(ValueError) as exception_info:
            validataclass_field(IntegerValidator(), init=False)

        assert str(exception_info.value) == 'Keyword argument "init" is not allowed in validator field.'

    @staticmethod
    def test_validataclass_field_with_default_factory_kwarg_raises_exception():
        """ Test that validataclass_field() does not allow the 'default_factory' keyword argument. """
        with pytest.raises(ValueError) as exception_info:
            validataclass_field(IntegerValidator(), default_factory=list)

        assert str(exception_info.value) == \
               'Keyword argument "default_factory" is not allowed in validator field (use default=DefaultFactory(...) instead).'


class ValidatorDataclassTest:
    """ Tests for the @validataclass decorator. """

    @staticmethod
    def test_validataclass_without_kwargs():
        """ Create a dataclass using @validataclass and check that all fields with metadata are created correctly. """

        @validataclass
        class UnitTestValidatorDataclass:
            foo: int = IntegerValidator()
            bar: Optional[int] = Noneable(IntegerValidator())
            baz: Optional[str] = validataclass_field(StringValidator(), default=None)

        # Check that @validataclass actually created a dataclass (i.e. used @dataclass on the class)
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
    def test_validataclass_with_kwargs():
        """ Create a dataclass using @validataclass(...) with arguments and check that they are passed to @dataclass(). """

        # Create two dataclasses, one without any arguments and one with unsafe_hash=True. The first won't have a __hash__ function,
        # but the latter will have one. We can use this to check that the argument was really passed to @dataclass.

        @validataclass()
        class FooDataclass:
            foo: int = IntegerValidator()

        @validataclass(unsafe_hash=True)
        class BarDataclass:
            foo: int = IntegerValidator()

        # Check that @validataclass actually created a dataclass (i.e. used @dataclass on the class)
        assert dataclasses.is_dataclass(FooDataclass)
        assert dataclasses.is_dataclass(BarDataclass)

        # Check if __hash__ exists
        assert FooDataclass.__hash__ is None
        assert BarDataclass.__hash__ is not None

    @staticmethod
    def test_validataclass_with_tuples():
        """ Create a dataclass using @validataclass with tuple syntax for setting Defaults. """

        @validataclass
        class UnitTestValidatorDataclass:
            foo: int = (IntegerValidator(), NoDefault)
            bar: int = (IntegerValidator(), Default(42))
            baz: Optional[int] = (IntegerValidator(), Default(None))

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
    def test_validataclass_with_non_init_fields():
        """ Create a dataclass using @validataclass with fields that have init=False. """

        @validataclass
        class UnitTestValidatorDataclass:
            # Some validated field
            validated: int = IntegerValidator()

            # Non-init field
            non_init: int = dataclasses.field(init=False, default=1)

        # Get fields from dataclass
        fields = dataclasses.fields(UnitTestValidatorDataclass)  # noqa

        # Check names and types of all fields
        assert [f.name for f in fields] == ['validated', 'non_init']
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

    # Subclassing / inheritance

    @staticmethod
    def test_validataclass_subclassing_defaults():
        """ Test the @validataclass decorator with a subclassed validataclass with different defaults. """

        @validataclass
        class BaseClass:
            # Required fields
            required1: int = IntegerValidator()
            required2: int = IntegerValidator()
            required3: int = IntegerValidator()
            required4: int = IntegerValidator()

            # Optional fields
            optional1: Optional[int] = (IntegerValidator(), Default(None))
            optional2: Optional[int] = (IntegerValidator(), Default(None))
            optional3: int = (IntegerValidator(), Default(3))
            optional4: Union[UnsetValueType, int] = (IntegerValidator(), DefaultUnset)

        @validataclass
        class SubClass(BaseClass):
            # Skipped fields must be still present and unchanged in subclass
            # required1: Unchanged
            # optional1: Unchanged

            # Required fields that are optional now
            required2: int = Default(42)
            required3: Optional[int] = Default(None)
            required4: Union[UnsetValueType, int] = DefaultUnset

            # Optional fields that are required now or have new defaults
            optional2: int = NoDefault
            optional3: Union[UnsetValueType, int] = DefaultUnset
            optional4: int = Default(42)

        # Get fields from dataclass
        fields = {field.name: field for field in dataclasses.fields(SubClass)}  # noqa

        # Check that all fields exist
        assert set(fields.keys()) == \
               {'required1', 'required2', 'required3', 'required4', 'optional1', 'optional2', 'optional3', 'optional4'}

        # Check type annotations
        assert all(fields[field].type is int for field in ['required1', 'required2', 'optional2', 'optional4'])
        assert all(fields[field].type is Optional[int] for field in ['required3', 'optional1'])
        assert all(fields[field].type is Union[UnsetValueType, int] for field in ['required4', 'optional3'])

        # Check validators
        assert all(type(field.metadata.get('validator')) is IntegerValidator for field in fields.values())

        # Check defaults for fields that are (now) required
        assert 'validator_default' not in fields['required1'].metadata
        assert 'validator_default' not in fields['optional2'].metadata

        # Check defaults for (now) optional fields
        assert_field_default(fields['required2'], default_value=42)
        assert_field_default(fields['required3'], default_value=None)
        assert_field_default(fields['optional1'], default_value=None)
        assert_field_default(fields['optional4'], default_value=42)
        assert fields['required4'].metadata.get('validator_default') is DefaultUnset
        assert fields['optional3'].metadata.get('validator_default') is DefaultUnset

    @staticmethod
    def test_validataclass_subclassing_validators():
        """ Test the @validataclass decorator with a subclassed validataclass with different validators and new fields. """

        @validataclass
        class BaseClass:
            # Required fields
            required1: int = IntegerValidator()
            required2: int = IntegerValidator()

            # Optional fields
            optional1: int = (IntegerValidator(), Default(3))
            optional2: int = (IntegerValidator(), Default(3))

        @validataclass
        class SubClass(BaseClass):
            # Required fields
            required1: str = StringValidator()
            required2: Optional[str] = (StringValidator(), Default(None))

            # Optional fields
            optional1: str = StringValidator()
            optional2: Optional[str] = (StringValidator(), Default(None))

            # New fields
            new1: str = StringValidator()
            new2: Optional[str] = (StringValidator(), Default(None))

        # Get fields from dataclass
        fields = {field.name: field for field in dataclasses.fields(SubClass)}  # noqa

        # Check that all fields exist
        assert set(fields.keys()) == {'required1', 'required2', 'optional1', 'optional2', 'new1', 'new2'}

        # Check type annotations
        assert all(fields[field].type is str for field in ['required1', 'optional1', 'new1'])
        assert all(fields[field].type is Optional[str] for field in ['required2', 'optional2', 'new2'])

        # Check validators
        assert all(type(field.metadata.get('validator')) is StringValidator for field in fields.values())

        # Check defaults for fields that are (now) required
        assert ('validator_default' not in fields[field].metadata for field in ['required1', 'optional1', 'new1'])

        # Check defaults for (now) optional fields
        assert_field_default(fields['required2'], default_value=None)
        assert_field_default(fields['optional2'], default_value=None)
        assert_field_default(fields['new2'], default_value=None)

    @staticmethod
    def test_validataclass_subclassing_with_non_init_fields():
        """ Test the @validataclass decorator with a subclass of a validataclass with fields that have init=False. """

        @validataclass
        class BaseClass:
            # Some validated field
            validated: int = IntegerValidator()

            # Non-init field
            non_init: int = dataclasses.field(init=False, default=1)

        @validataclass
        class SubClass(BaseClass):
            # Modify the validated field
            validated: int = (IntegerValidator(), Default(42))

        # Get fields from dataclass
        fields = {field.name: field for field in dataclasses.fields(SubClass)}  # noqa

        # Check names and types of all fields
        assert set(fields.keys()) == {'validated', 'non_init'}
        assert all(f.type is int for f in fields.values())

        # Check 'init' value
        assert fields['validated'].init is True
        assert fields['non_init'].init is False

        # Check that non-init field has regular default value
        assert fields['validated'].default is dataclasses.MISSING
        assert fields['non_init'].default == 1

        # Check that non-init field has no validator metadata
        assert type(fields['validated'].metadata.get('validator')) is IntegerValidator
        assert 'validator' not in fields['non_init'].metadata

        # Check default for modified field
        assert_field_default(fields['validated'], default_value=42)

    # Error cases

    @staticmethod
    def test_validataclass_with_invalid_values():
        """ Test that @validataclass raises exceptions when a field is not predefined (e.g. with field()) and has no Validator. """

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            @validataclass
            class InvalidDataclass:
                foo: int

        assert str(exception_info.value) == 'Dataclass field "foo" must specify a Validator.'

    @staticmethod
    @pytest.mark.parametrize(
        'field_tuple, expected_exception_msg', [
            (
                # None, missing validator
                None,
                'Dataclass field "foo" must specify a Validator.',
            ),
            (
                # Default only, missing validator
                (Default(3)),
                'Dataclass field "foo" must specify a Validator.',
            ),
            (
                # Tuple with invalid length
                (IntegerValidator(), Default(5), Default(3)),
                'Dataclass field "foo": Unexpected number of arguments.',
            ),
            (
                # Invalid argument type (without validator)
                3,
                'Dataclass field "foo": Unexpected type of argument: int',
            ),
            (
                # Invalid argument type (with validator)
                (IntegerValidator(), 5),
                'Dataclass field "foo": Unexpected type of argument: int',
            ),
            (
                # Two validators in a tuple
                (IntegerValidator(), StringValidator()),
                'Dataclass field "foo": Only one Validator can be specified.',
            ),
            (
                # Two defaults in a tuple
                (Default(3), Default(None)),
                'Dataclass field "foo": Only one Default can be specified.',
            ),
        ]
    )
    def test_validataclass_with_invalid_field_tuples(field_tuple, expected_exception_msg):
        """ Test that @validataclass raises exceptions for with various invalid tuples. """
        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            @validataclass
            class InvalidDataclass:
                foo: int = field_tuple

        assert str(exception_info.value) == expected_exception_msg

    @staticmethod
    def test_validataclass_with_init_vars_exception():
        """ Test that @validataclass raises an exception when it detects InitVars (because they don't work currently). """
        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            @validataclass
            class InvalidDataclass:
                foo: dataclasses.InitVar[int] = IntegerValidator()

        assert str(exception_info.value) == 'Dataclass field "foo": InitVars currently not supported by DataclassValidator.'
