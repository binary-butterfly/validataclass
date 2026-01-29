"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses

import pytest
from typing_extensions import override

from tests.test_utils import UNSET_PARAMETER
from tests.unit.dataclasses._helpers import assert_field_default, assert_field_no_default, get_dataclass_fields
from validataclass.dataclasses import BaseDefault, Default, DefaultFactory, DefaultUnset, NoDefault, validataclass_field
from validataclass.helpers import UnsetValue
from validataclass.validators import IntegerValidator


class ValidataclassFieldTest:
    """ Tests for the validataclass_field() helper method. """

    @staticmethod
    @pytest.mark.parametrize(
        'param_default',
        [
            # Parameter is not set at all
            UNSET_PARAMETER,

            # Parameter is set explicitly to these sentinel values that mean "no default"
            dataclasses.MISSING,
            NoDefault,
        ],
    )
    def test_validataclass_field_without_default(param_default):
        """ Test validataclass_field function on its own, without a default value (implicitly and explicitly). """
        # Create field
        params = {} if param_default is UNSET_PARAMETER else {'default': param_default}
        field = validataclass_field(IntegerValidator(), **params)

        # Check field metadata
        assert type(field.metadata.get('validator')) is IntegerValidator
        assert 'validator_default' not in field.metadata

        # Check field default
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING

    @staticmethod
    @pytest.mark.parametrize(
        'param_default, expected_default',
        [
            # Explicit Default objects
            (Default(42), 42),
            (Default(None), None),
            (Default(UnsetValue), UnsetValue),
            (DefaultUnset, UnsetValue),

            # Regular values (automatically converted to Default objects)
            (42, 42),
            (None, None),
            (UnsetValue, UnsetValue),
        ],
    )
    def test_validataclass_field_with_default(param_default, expected_default):
        """ Test validataclass_field function on its own, with various static default values. """
        # Create field
        field = validataclass_field(IntegerValidator(), default=param_default)

        # Check field metadata
        metadata_validator = field.metadata.get('validator')
        metadata_default = field.metadata.get('validator_default')

        assert type(metadata_validator) is IntegerValidator
        assert type(metadata_default) is Default
        assert metadata_default.get_value() == expected_default
        assert metadata_default.needs_factory() is False

        # Check field default and default_factory
        assert field.default == expected_default
        assert field.default_factory is dataclasses.MISSING

    @staticmethod
    @pytest.mark.parametrize(
        'param_default, expected_default, expected_default_cls',
        [
            # Default object with mutable value (should result in a default_factory)
            (Default([]), [], Default),

            # DefaultFactory object
            (DefaultFactory(lambda: 3), 3, DefaultFactory),
        ],
    )
    def test_validataclass_field_with_default_factory(param_default, expected_default, expected_default_cls):
        """ Test validataclass_field function on its own, with default objects that require a default_factory. """
        # Create field
        field = validataclass_field(IntegerValidator(), default=param_default)

        # Check field metadata
        metadata_validator = field.metadata.get('validator')
        metadata_default = field.metadata.get('validator_default')

        assert type(metadata_validator) is IntegerValidator
        assert type(metadata_default) is expected_default_cls
        assert metadata_default.get_value() == expected_default
        assert metadata_default.needs_factory() is True

        # Check field default and default_factory
        assert field.default is dataclasses.MISSING
        assert field.default_factory is not dataclasses.MISSING
        assert field.default_factory() == expected_default

    @staticmethod
    def test_validataclass_field_with_custom_default_class():
        """ Test validataclass_field() on its own with a custom default class (which generates a default factory). """

        # Create a custom Default subclass
        class CustomDefault(BaseDefault[int]):
            counter: int = 0

            @override
            def get_value(self) -> int:
                self.counter += 1
                return self.counter

            @override
            def needs_factory(self) -> bool:
                return True

        # Create field
        field = validataclass_field(IntegerValidator(), default=CustomDefault())

        # Check field metadata
        metadata_validator = field.metadata.get('validator')
        metadata_default = field.metadata.get('validator_default')

        assert type(metadata_validator) is IntegerValidator
        assert type(metadata_default) is CustomDefault
        assert metadata_default.get_value() == 1
        assert metadata_default.get_value() == 2
        assert metadata_default.needs_factory() is True

        # Check field default and default_factory
        assert field.default is dataclasses.MISSING
        assert field.default_factory is not dataclasses.MISSING
        assert field.default_factory() == 3
        assert field.default_factory() == 4

    @staticmethod
    def test_validataclass_field_with_metadata():
        """ Test validataclass_field function on its own, with custom metadata. """
        # Create field with custom metadata (validataclass metadata will be overwritten by the function)
        field = validataclass_field(
            IntegerValidator(),
            default=Default(42),
            metadata={
                'unittest': 123,
                'validator': 'gets overwritten',
                'validator_default': 'gets overwritten',
            },
        )

        # Check field metadata
        metadata_validator = field.metadata.get('validator')
        metadata_default = field.metadata.get('validator_default')

        assert type(metadata_validator) is IntegerValidator
        assert type(metadata_default) is Default
        assert metadata_default.get_value() == 42
        assert field.metadata.get('unittest') == 123

    @staticmethod
    def test_validataclass_fields_in_dataclass():
        """ Create a dataclass with validataclass_field() and check that the fields are created correctly. """

        @dataclasses.dataclass
        class UnitTestDataclass:
            foo: int = validataclass_field(IntegerValidator())
            bar: int = validataclass_field(IntegerValidator(), default=Default(1))
            baz: int = validataclass_field(IntegerValidator(), default=42)

        # Get fields from dataclass
        fields = get_dataclass_fields(UnitTestDataclass)

        # Check names and types of all fields
        assert list(fields.keys()) == ['foo', 'bar', 'baz']
        assert all(f.type is int for f in fields.values())

        # Check that all fields have an IntegerValidator object as validator
        assert all(type(f.metadata.get('validator')) is IntegerValidator for f in fields.values())

        # Check field defaults
        assert_field_no_default(fields['foo'])
        assert_field_default(fields['bar'], default_value=1)
        assert_field_default(fields['baz'], default_value=42)

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

        assert (
            str(exception_info.value)
            == 'Keyword argument "default_factory" is not allowed in validator field (use default=DefaultFactory(...) '
               'instead).'
        )
