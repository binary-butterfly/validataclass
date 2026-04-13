"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
from typing import Any

import pytest
from typing_extensions import override

from tests.unit.dataclasses._helpers import assert_field_default, assert_field_no_default, get_dataclass_fields
from validataclass.dataclasses import BaseDefault, Default, DefaultFactory, DefaultUnset, NoDefault, validataclass_field
from validataclass.helpers import UnsetValue
from validataclass.validators import IntegerValidator, Validator


# Here we are testing the validataclass_field() function on its own. It usually doesn't make sense to use this function
# outside the context of a dataclass, which is why the annotated return type doesn't match what it actually returns
# (see note in validataclass_field module).
# However, for testing, we need the actual return type (otherwise type checkers will be very unhappy about this file),
# so we're actually using a wrapper here that fixes the type. I know it's ugly, but it's just for testing.
# (We'll keep the typing as simple as possible and skip the overloads, though.)
def typed_validataclass_field(
    validator: Validator[Any],
    *,
    default: Any = NoDefault,
    **kwargs: Any,
) -> dataclasses.Field[Any]:
    return validataclass_field(validator, default=default, **kwargs)  # type: ignore[no-any-return]


class ValidataclassFieldTest:
    """ Tests for the validataclass_field() helper method. """

    @staticmethod
    @pytest.mark.parametrize('explicit_no_default', [True, False])
    def test_validataclass_field_without_default(explicit_no_default):
        """ Test validataclass_field function on its own, without a default value (implicitly and explicitly). """
        # Create field
        if explicit_no_default:
            field = typed_validataclass_field(IntegerValidator(), default=NoDefault)
        else:
            field = typed_validataclass_field(IntegerValidator())

        # Check field metadata
        assert type(field.metadata.get('validator')) is IntegerValidator
        assert 'validator_default' not in field.metadata

        # Check field default
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING

    @staticmethod
    @pytest.mark.parametrize(
        'param_default, expected_default, needs_factory',
        [
            # Static default values that don't need a factory
            (Default(42), 42, False),
            (Default(None), None, False),
            (Default(UnsetValue), UnsetValue, False),
            (DefaultUnset, UnsetValue, False),

            # Default object with mutable value (should result in a default factory)
            (Default([]), [], True),

            # DefaultFactory object
            (DefaultFactory(lambda: 3), 3, True),
        ],
    )
    def test_validataclass_field_with_default(param_default, expected_default, needs_factory):
        """ Test validataclass_field function on its own, with various static default values and default factories. """
        # Create field
        field = typed_validataclass_field(IntegerValidator(), default=param_default)

        # Check field metadata
        metadata_validator = field.metadata.get('validator')
        metadata_default = field.metadata.get('validator_default')

        assert type(metadata_validator) is IntegerValidator
        assert metadata_default is not None
        assert type(metadata_default) is type(param_default)
        assert metadata_default.get_value() == expected_default
        assert metadata_default.needs_factory() == needs_factory

        # Check field default and default_factory
        if needs_factory:
            assert field.default is dataclasses.MISSING
            assert callable(field.default_factory)
            assert field.default_factory() == expected_default
        else:
            assert field.default == expected_default
            assert field.default_factory is dataclasses.MISSING

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
        field = typed_validataclass_field(IntegerValidator(), default=CustomDefault())

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
        field = typed_validataclass_field(
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
            no_default_implicit: int = validataclass_field(IntegerValidator())
            no_default_explicit: int = validataclass_field(IntegerValidator(), default=NoDefault)
            default_int: int = validataclass_field(IntegerValidator(), default=Default(1))
            default_none: int | None = validataclass_field(IntegerValidator(), default=Default(None))

        # Get fields from dataclass
        fields = get_dataclass_fields(UnitTestDataclass)

        # Check types of all fields
        assert len(fields.keys()) == 4
        assert fields['no_default_implicit'].type is int
        assert fields['no_default_explicit'].type is int
        assert fields['default_int'].type is int
        assert fields['default_none'].type == int | None

        # Check that all fields have an IntegerValidator object as validator
        assert all(type(f.metadata.get('validator')) is IntegerValidator for f in fields.values())

        # Check field defaults
        assert_field_no_default(fields['no_default_implicit'])
        assert_field_no_default(fields['no_default_explicit'])
        assert_field_default(fields['default_int'], default_value=1)
        assert_field_default(fields['default_none'], default_value=None)

    @staticmethod
    def test_validataclass_field_with_init_kwarg_raises_exception():
        """ Test that validataclass_field() does not allow the 'init' keyword argument. """
        with pytest.raises(ValueError) as exception_info:
            validataclass_field(IntegerValidator(), init=False)

        assert str(exception_info.value) == 'Keyword argument "init" is not allowed in validataclass_field.'

    @staticmethod
    def test_validataclass_field_with_default_factory_kwarg_raises_exception():
        """ Test that validataclass_field() does not allow the 'default_factory' keyword argument. """
        with pytest.raises(ValueError) as exception_info:
            validataclass_field(IntegerValidator(), default_factory=list)

        assert (
            str(exception_info.value)
            == 'Keyword argument "default_factory" is not allowed in validataclass_field (use '
               'default=DefaultFactory(...) instead).'
        )

    @staticmethod
    @pytest.mark.parametrize('param_default', [42, '', None])
    def test_validataclass_field_with_raw_defaults_is_deprecated(param_default: int | str | None) -> None:
        """ Test that validataclass_field() with raw default values is deprecated. """
        # Create field and test that it generates a deprecation warning
        with pytest.deprecated_call(match='Please use default objects instead'):
            field = typed_validataclass_field(IntegerValidator(), default=param_default)

        # Check field metadata
        metadata_validator = field.metadata.get('validator')
        metadata_default = field.metadata.get('validator_default')

        assert type(metadata_validator) is IntegerValidator
        assert type(metadata_default) is Default
        assert metadata_default.get_value() == param_default

        # Check field default and default_factory
        assert field.default == param_default
        assert field.default_factory is dataclasses.MISSING

    @staticmethod
    def test_validataclass_field_with_dataclasses_missing_is_deprecated():
        """ Test that validataclass_field() with `default=dataclasses.MISSING` is deprecated. """
        # Create field and test that it generates a deprecation warning
        with pytest.deprecated_call(match='Please use `default=NoDefault` instead'):
            field = typed_validataclass_field(IntegerValidator(), default=dataclasses.MISSING)

        # Check field metadata
        assert type(field.metadata.get('validator')) is IntegerValidator
        assert 'validator_default' not in field.metadata

        # Check field default
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
