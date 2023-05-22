"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List

import pytest

from tests.test_utils import UnitTestContextValidator
from validataclass.dataclasses import validataclass, validataclass_field, Default, DefaultFactory, DefaultUnset
from validataclass.exceptions import ValidationError, RequiredValueError, DictFieldsValidationError, DataclassPostValidationError, \
    InvalidValidatorOptionException, DataclassValidatorFieldException
from validataclass.helpers import UnsetValue, OptionalUnset
from validataclass.validators import DataclassValidator, DecimalValidator, IntegerValidator, StringValidator, ListValidator


# Simple example dataclass

@validataclass
class UnitTestDataclass:
    """
    Simple dataclass for testing DataclassValidator.
    """
    name: str = StringValidator()
    color: str = (StringValidator(), Default('unknown color'))
    amount: int = IntegerValidator()
    weight: Decimal = DecimalValidator()


# More complex / nested dataclass

@validataclass
class UnitTestNestedDataclass:
    """
    Complex dataclass that contains other dataclasses, used for testing nested DataclassValidators.
    """
    name: str = StringValidator()
    test_fruit: UnitTestDataclass = DataclassValidator(UnitTestDataclass)
    test_vegetable: Optional[UnitTestDataclass] = validataclass_field(DataclassValidator(UnitTestDataclass), default=None)


# Dataclass with non-init field and __post_init__() method

@validataclass
class UnitTestPostInitDataclass:
    """
    Dataclass with a non-init field that is set in a `__post_init__()` method (which also does some post-validation).
    """
    # Normal validated fields
    base: str = StringValidator()
    count: int = IntegerValidator()
    # Non-init field: Field exists in the resulting class, but is *not* set in __init__()
    result: str = field(init=False)

    def __post_init__(self):
        # Check conditions
        if self.count < 0:
            # (Note: Validating that a number is positive should not be in __post_init__ of course, this is just an example for testing)
            raise DataclassPostValidationError(field_errors={
                'count': ValidationError(code='invalid_count', reason='Count must be positive.'),
            })

        # Set non-init field
        self.result = self.count * self.base


# Dataclasses with __post_validate__() method (with and without context-sensitive validation)

@validataclass
class UnitTestPostValidationDataclass:
    """
    Dataclass to test post-validation using the `__post_validate__()` method.
    """
    start: int = IntegerValidator()
    end: int = IntegerValidator()

    def __post_validate__(self):
        if self.start > self.end:
            raise ValidationError(code='invalid_range', reason='"start" must be smaller than or equal to "end".')


@validataclass
class UnitTestContextSensitiveDataclass:
    """
    Dataclass to test context-sensitive post-validation.

    The class has a field "name" that is always required, and a field "value" which usually is optional, but required
    when the context argument "value_required" is set.
    """
    name: str = UnitTestContextValidator()
    value: Optional[int] = (IntegerValidator(), Default(None))

    def __post_validate__(self, *, value_required: bool = False):
        if value_required and self.value is None:
            raise DataclassPostValidationError(field_errors={
                'value': RequiredValueError(reason='Value is required in this context.'),
            })


@validataclass
class UnitTestContextSensitiveDataclassWithPosArgs(UnitTestContextSensitiveDataclass):
    """
    Dataclass with a __post_validate__() method that takes *positional* arguments. This should work, but emit a warning.
    """

    # Same as UnitTestContextSensitiveDataclass, but with positional arguments
    def __post_validate__(self, value_required: bool = False):
        super().__post_validate__(value_required=value_required)


# Regex-escaped warning text emitted when using __post_validate__ of the dataclass above
POST_VALIDATE_POS_ARGS_WARNING = \
    r'UnitTestContextSensitiveDataclassWithPosArgs\.__post_validate__\(\) is defined with positional arguments'


@validataclass
class UnitTestContextSensitiveDataclassWithVarKwargs:
    """
    Dataclass with a __post_validate__() method that takes fixed *and* variable keyword arguments (`**kwargs`).

    This class only has one validated field "name". Additionally it takes two context parameters "ctx_a" and "ctx_b", as
    well as arbitrary keyword arguments, which will be written into the attributes "ctx_a", "ctx_b" and "extra_kwargs"
    respectively.
    """
    name: str = UnitTestContextValidator()

    # These are no validated fields, just attributes that are populated by __post_validate__
    ctx_a = None
    ctx_b = None
    extra_kwargs = None

    def __post_validate__(self, *, ctx_a: str = '', ctx_b: str = '', **kwargs):
        self.ctx_a = ctx_a
        self.ctx_b = ctx_b
        self.extra_kwargs = kwargs


class DataclassValidatorTest:
    # Tests for DataclassValidator with a simple dataclass

    @staticmethod
    def test_dataclass_valid():
        """ Validate a dictionary as a dataclass, using valid data. """
        validator = DataclassValidator(UnitTestDataclass)
        validated_data = validator.validate({
            'name': 'banana',
            'color': 'yellow',
            'amount': 10,
            'weight': '1.234',
            # Unknown fields will be ignored
            'unknown_field': 'unknown_value',
        })

        assert type(validated_data) is UnitTestDataclass
        assert validated_data.name == 'banana'
        assert validated_data.color == 'yellow'
        assert validated_data.amount == 10
        assert validated_data.weight == Decimal('1.234')

    @staticmethod
    def test_dataclass_invalid_none():
        """ Test a DataclassValidator with 'None' as input. """
        validator = DataclassValidator(UnitTestDataclass)
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_dataclass_invalid():
        """ Test a DataclassValidator with invalid and missing data. """
        validator = DataclassValidator(UnitTestDataclass)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'name': None,
                'color': 5,
                'amount': 'drei',
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'name': {'code': 'required_value'},
                'color': {'code': 'invalid_type', 'expected_type': 'str'},
                'amount': {'code': 'invalid_type', 'expected_type': 'int'},
                'weight': {'code': 'required_field'},
            },
        }

    @staticmethod
    def test_dataclass_optional_field():
        """ Test optional fields in dataclasses. """
        validator = DataclassValidator(UnitTestDataclass)
        validated_data = validator.validate({
            'name': 'apple',
            'amount': 3,
            'weight': '0.5',
            # Leaving out optional field 'color'
        })

        assert type(validated_data) is UnitTestDataclass
        assert validated_data.name == 'apple'
        # Check the default value
        assert validated_data.color == 'unknown color'
        assert validated_data.amount == 3
        assert validated_data.weight == Decimal('0.5')

    @staticmethod
    def test_dataclass_with_various_default_classes():
        """ Test DataclassValidator with a dataclass with all kinds of Default objects (Default, DefaultUnset, DefaultFactory). """

        def counter():
            """ Function that counts up every time it is called and saves the current number as an attribute of itself. """
            current = getattr(counter, 'current', 0) + 1
            setattr(counter, 'current', current)
            return current

        @validataclass
        class DataclassWithDefaults:
            default_str: str = (StringValidator(), Default('example default'))
            default_list: List[int] = (ListValidator(IntegerValidator()), Default([]))
            default_counter: int = (IntegerValidator(), DefaultFactory(counter))
            default_unset: OptionalUnset[str] = (StringValidator(), DefaultUnset)

        validator = DataclassValidator(DataclassWithDefaults)

        # Validate multiple objects to check that the counter actually counts up
        validated_objects = {i: validator.validate({}) for i in (1, 2, 3)}

        for i, validated_data in validated_objects.items():
            assert validated_data.default_str == 'example default'
            assert validated_data.default_list == []
            assert validated_data.default_counter == i
            assert validated_data.default_unset is UnsetValue

        # Verify that the default list was deepcopied
        assert validated_objects[1].default_list is not validated_objects[2].default_list is not validated_objects[3].default_list

    # Tests for DataclassValidator with context arguments

    @staticmethod
    def test_validation_with_context_arguments():
        """ Test that DataclassValidator passes context arguments down to the field validators. """

        @validataclass
        class DataclassWithContextSensitiveValidators:
            field1: str = UnitTestContextValidator(prefix='1')
            field2: str = UnitTestContextValidator(prefix='2')

        validator = DataclassValidator(DataclassWithContextSensitiveValidators)
        validated_data = validator.validate({
            'field1': 'apple',
            'field2': 'banana',
        }, foo=42)

        assert validated_data.field1 == "[1] apple / {'foo': 42}"
        assert validated_data.field2 == "[2] banana / {'foo': 42}"

    # Tests for more complex and nested validators using dataclasses

    @staticmethod
    def test_nested_dataclasses_valid():
        """ Validate nested dataclasses. """
        validator = DataclassValidator(UnitTestNestedDataclass)
        validated_data = validator.validate({
            'name': 'something with bananas',
            'test_fruit': {
                'name': 'banana',
                'amount': 3,
                'weight': '0.456',
                # Leaving out optional field 'color'
            },
            # Leaving out optional field 'test_vegetable'
        })

        # Check outer dataclass
        assert type(validated_data) is UnitTestNestedDataclass
        assert validated_data.name == 'something with bananas'

        # Check inner dataclass
        assert type(validated_data.test_fruit) is UnitTestDataclass
        assert validated_data.test_fruit.name == 'banana'
        assert validated_data.test_fruit.amount == 3
        assert validated_data.test_fruit.weight == Decimal('0.456')
        assert validated_data.test_fruit.color == 'unknown color'

        # Check default value
        assert validated_data.test_vegetable is None

    @staticmethod
    def test_nested_dataclasses_invalid():
        """ Validate nested dataclasses with invalid data. """
        validator = DataclassValidator(UnitTestNestedDataclass)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'name': 123,
                # Leaving out *required* field 'test_fruit'
                'test_vegetable': {
                    'name': 'banana',
                    'amount': 'banananana',
                },
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'name': {'code': 'invalid_type', 'expected_type': 'str'},
                'test_fruit': {'code': 'required_field'},
                'test_vegetable': {
                    'code': 'field_errors',
                    'field_errors': {
                        'amount': {'code': 'invalid_type', 'expected_type': 'int'},
                        'weight': {'code': 'required_field'},
                    },
                },
            },
        }

    # Test dataclasses with non-init fields and __post_init__() methods

    @staticmethod
    def test_dataclass_with_post_init():
        """ Validate dataclasses with non-init fields and a __post_init__() method. """
        validator = DataclassValidator(UnitTestPostInitDataclass)
        validated_data = validator.validate({
            'base': 'meow',
            'count': 3,
        })

        assert validated_data.base == 'meow'
        assert validated_data.count == 3
        assert validated_data.result == 'meowmeowmeow'

    @staticmethod
    def test_dataclass_with_post_init_field_errors():
        """ Validate dataclasses with non-init fields and a __post_init__() method that raises a DataclassPostValidationError. """
        validator = DataclassValidator(UnitTestPostInitDataclass)

        with pytest.raises(DataclassPostValidationError) as exception_info:
            validator.validate({
                'base': 'meow',
                'count': -1,
            })

        assert exception_info.value.to_dict() == {
            'code': 'post_validation_errors',
            'field_errors': {
                'count': {
                    'code': 'invalid_count',
                    'reason': 'Count must be positive.',
                },
            },
        }

    @staticmethod
    def test_dataclass_with_post_init_wrapped_error():
        """ Validate dataclasses with non-init fields and a __post_init__() method that raises an arbitrary ValidationError. """

        @validataclass
        class PostInitDataclass:
            a: int = IntegerValidator()
            b: int = IntegerValidator()
            c: int = IntegerValidator()

            def __post_init__(self):
                if self.a + self.b + self.c != 0:
                    raise ValidationError(code='example_error', reason='Sum of a, b, c must always be zero!')

        validator = DataclassValidator(PostInitDataclass)

        with pytest.raises(DataclassPostValidationError) as exception_info:
            validator.validate({
                'a': 1,
                'b': 2,
                'c': 3,
            })

        assert exception_info.value.to_dict() == {
            'code': 'post_validation_errors',
            'error': {
                'code': 'example_error',
                'reason': 'Sum of a, b, c must always be zero!',
            },
        }

    @staticmethod
    def test_dataclass_with_post_init_internal_error():
        """ Validate dataclasses with non-init fields and a __post_init__() method that raises non-ValidationError exception. """

        @validataclass
        class PostInitDataclass:
            a: int = IntegerValidator()
            b: int = IntegerValidator()
            c: float = field(init=False)

            def __post_init__(self):
                # This will result in a divide-by-zero error if b is zero.
                # Real code should always explicitly check the value of b and raise a real ValidationError!
                self.c = self.a / self.b

        validator = DataclassValidator(PostInitDataclass)

        with pytest.raises(ZeroDivisionError):
            # Let's cause a divide-by-zero error!
            validator.validate({
                'a': 1,
                'b': 0,
            })

    # Test dataclasses with __post_validate__() method (with and without context-sensitive validation)

    @staticmethod
    def test_dataclass_with_post_validate():
        """ Validate dataclass with __post_validate__() method. """
        validator = DataclassValidator(UnitTestPostValidationDataclass)
        validated_data = validator.validate({
            'start': 3,
            'end': 4,
        })

        assert validated_data.start == 3
        assert validated_data.end == 4

    @staticmethod
    def test_dataclass_with_post_validate_invalid():
        """ Validate dataclass with __post_validate__() method, with invalid input. """
        validator = DataclassValidator(UnitTestPostValidationDataclass)

        with pytest.raises(DataclassPostValidationError) as exception_info:
            validator.validate({
                'start': 3,
                'end': 2,
            })

        assert exception_info.value.to_dict() == {
            'code': 'post_validation_errors',
            'error': {
                'code': 'invalid_range',
                'reason': '"start" must be smaller than or equal to "end".',
            },
        }

    @staticmethod
    @pytest.mark.parametrize(
        'validate_kwargs, input_data, expected_value',
        [
            # No context arguments
            ({}, {'name': 'banana'}, None),
            ({}, {'name': 'banana', 'value': 13}, 13),

            # Context argument "value_required"
            ({'value_required': False}, {'name': 'banana'}, None),
            ({'value_required': False}, {'name': 'banana', 'value': 13}, 13),
            ({'value_required': True}, {'name': 'banana', 'value': 13}, 13),

            # Test that all context arguments are passed to other validators as well
            ({'value_required': False, 'foo': 42}, {'name': 'banana'}, None),
        ]
    )
    def test_dataclass_with_context_sensitive_post_validate(validate_kwargs, input_data, expected_value):
        """ Validate dataclass with a context-sensitive __post_validate__() method. """
        validator = DataclassValidator(UnitTestContextSensitiveDataclass)
        validated_data = validator.validate(input_data, **validate_kwargs)

        assert validated_data.name == f"banana / {validate_kwargs}"
        assert validated_data.value == expected_value

    @staticmethod
    def test_dataclass_with_context_sensitive_post_validate_invalid():
        """ Validate dataclass with a context-sensitive __post_validate__() method, with invalid input. """
        validator = DataclassValidator(UnitTestContextSensitiveDataclass)

        # Without context arguments
        with pytest.raises(DataclassPostValidationError) as exception_info:
            validator.validate({'name': 'banana'}, value_required=True)

        assert exception_info.value.to_dict() == {
            'code': 'post_validation_errors',
            'field_errors': {
                'value': {
                    'code': 'required_value',
                    'reason': 'Value is required in this context.',
                },
            },
        }

    @staticmethod
    def test_dataclass_with_context_sensitive_post_validate_with_pos_args():
        """ Validate dataclass with a __post_validate__() method that accepts positional arguments. """
        validator = DataclassValidator(UnitTestContextSensitiveDataclassWithPosArgs)

        with pytest.warns(UserWarning, match=POST_VALIDATE_POS_ARGS_WARNING):
            validated_data = validator.validate({'name': 'banana', 'value': 13}, value_required=True, foo=42)

        assert validated_data.name == "banana / {'value_required': True, 'foo': 42}"
        assert validated_data.value == 13

    @staticmethod
    def test_dataclass_with_context_sensitive_post_validate_with_pos_args_invalid():
        """ Validate dataclass with a __post_validate__() method that accepts positional arguments, with invalid input. """
        validator = DataclassValidator(UnitTestContextSensitiveDataclassWithPosArgs)

        with pytest.raises(DataclassPostValidationError):
            with pytest.warns(UserWarning, match=POST_VALIDATE_POS_ARGS_WARNING):
                validator.validate({'name': 'banana'}, value_required=True)

    @staticmethod
    @pytest.mark.parametrize(
        'validate_kwargs, expected_ctx_a, expected_ctx_b, expected_extra_kwargs',
        [
            # No context arguments
            ({}, '', '', {}),

            # Only context parameters defined as keyword arguments in __post_validate__ (ctx_a, ctx_b)
            ({'ctx_a': 'foo'}, 'foo', '', {}),
            ({'ctx_b': 'bar'}, '', 'bar', {}),
            ({'ctx_b': 'bar', 'ctx_a': 'foo'}, 'foo', 'bar', {}),

            # Arbitrary context arguments not defined as keyword arguments in __post_validate__
            (
                {'some_value': 42},
                '',
                '',
                {'some_value': 42},
            ),
            (
                {'ctx_a': 'foo', 'some_value': 42},
                'foo',
                '',
                {'some_value': 42},
            ),
            (
                {'any_value': 3, 'ctx_a': 'foo', 'some_value': 42, 'ctx_b': 'bar'},
                'foo',
                'bar',
                {'any_value': 3, 'some_value': 42},
            ),
        ]
    )
    def test_dataclass_with_context_sensitive_post_validate_with_var_kwargs(
        validate_kwargs, expected_ctx_a, expected_ctx_b, expected_extra_kwargs,
    ):
        """ Validate dataclass with a context-sensitive __post_validate__() method that accepts arbitrary keyword arguments. """
        validator = DataclassValidator(UnitTestContextSensitiveDataclassWithVarKwargs)
        validated_data = validator.validate({'name': 'unit-test'}, **validate_kwargs)

        assert validated_data.name == f"unit-test / {validate_kwargs}"
        assert validated_data.ctx_a == expected_ctx_a
        assert validated_data.ctx_b == expected_ctx_b
        assert validated_data.extra_kwargs == expected_extra_kwargs

    # Test invalid validator options

    @staticmethod
    def test_invalid_dataclass_validator_without_dataclass():
        """ Test that a DataclassValidator cannot be created without a dataclass. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DataclassValidator()
        assert str(exception_info.value) == 'Parameter "dataclass_cls" must be specified (or set as class member in a subclass).'

    @staticmethod
    def test_invalid_dataclass_validator_with_invalid_dataclass():
        """ Test that a DataclassValidator cannot be created with a class that is not a dataclass. """

        class Foo:
            bar: int = IntegerValidator()

        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DataclassValidator(Foo)
        assert str(exception_info.value) == 'Parameter "dataclass_cls" must be a dataclass type.'

    @staticmethod
    def test_invalid_dataclass_validator_with_dataclass_instance():
        """ Test that a DataclassValidator cannot be created with an *instance* of a dataclass. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            dataclass_instance = UnitTestDataclass(name='bluenana', color='blue', amount=3, weight=Decimal('1.234'))
            DataclassValidator(dataclass_instance)

        assert str(exception_info.value) == 'Parameter "dataclass_cls" is a dataclass instance, but must be a dataclass type.'

    # Test DataclassValidator with incompatible dataclasses

    @staticmethod
    def test_dataclass_field_without_validator():
        """ Test that DataclassValidator only allows dataclasses where every field has a defined Validator. """

        @dataclass
        class IncompatibleDataclass:
            # No validator specified
            foo: str = 'unknown'

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            DataclassValidator(IncompatibleDataclass)
        assert str(exception_info.value) == 'Dataclass field "foo" has no defined Validator.'

    @staticmethod
    def test_dataclass_field_with_invalid_validator():
        """ Test that DataclassValidator only allows dataclasses where every field has a valid Validator. """

        @dataclass
        class IncompatibleDataclass:
            # Metadata contains 'validator' but it is not of type Validator
            foo: str = field(default='unknown', metadata={'validator': 'foobar'})

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            DataclassValidator(IncompatibleDataclass)
        assert str(exception_info.value) == 'Validator specified for dataclass field "foo" is not of type "Validator".'

    @staticmethod
    def test_dataclass_field_with_invalid_default():
        """ Test that DataclassValidator raises exceptions for fields with invalid 'validator_default' metadata. """

        @dataclass
        class IncompatibleDataclass:
            # Metadata contains 'validator_default' but it is not of type Default
            foo: str = field(default='unknown', metadata={'validator': StringValidator(), 'validator_default': 'foobar'})

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            DataclassValidator(IncompatibleDataclass)
        assert str(exception_info.value) == 'Default specified for dataclass field "foo" is not of type "Default".'
