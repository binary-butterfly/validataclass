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
from validataclass.dataclasses import Default, DefaultFactory, DefaultUnset, validataclass, validataclass_field
from validataclass.exceptions import (
    DataclassInvalidPreValidateSignatureException,
    DataclassPostValidationError,
    DataclassValidatorFieldException,
    DictFieldsValidationError,
    DictRequiredFieldError,
    InvalidValidatorOptionException,
    RequiredValueError,
    ValidationError,
)
from validataclass.helpers import UnsetValue, OptionalUnset
from validataclass.validators import (
    DataclassValidator,
    DecimalValidator,
    IntegerValidator,
    StringValidator,
    ListValidator,
)


# Simple example dataclass

@validataclass
class UnitTestDataclass:
    """
    Simple dataclass for testing DataclassValidator.
    """
    name: str = StringValidator()
    color: str = StringValidator(), Default('unknown color')
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
    test_vegetable: Optional[UnitTestDataclass] = \
        validataclass_field(DataclassValidator(UnitTestDataclass), default=None)


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
            # (Note: Validating that a number is positive should not be in __post_init__ of course, this is just an
            # example for testing)
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
    value: Optional[int] = IntegerValidator(), Default(None)

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


# Dataclasses with __pre_validate__() method (with and without context-sensitive validation)

@validataclass
class UnitTestPreValidateStaticMethodDataclass:
    """
    Dataclass with `__pre_validate__()` static method to map field names from camelCase to snake_case pre-validation.
    """
    example_str: str = StringValidator()
    example_int: int = IntegerValidator()

    @staticmethod
    def __pre_validate__(input_data: dict) -> dict:
        mapping = {
            'exampleStr': 'example_str',
            'exampleInt': 'example_int',
        }

        for from_key, to_key in mapping.items():
            if from_key in input_data:
                input_data[to_key] = input_data.pop(from_key)

        return input_data


@validataclass
class UnitTestPreValidateClassMethodDataclass:
    """
    Dataclass with `__pre_validate__()` class method to map field names from camelCase to snake_case pre-validation.
    """
    __key_mapping = {
        'exampleStr': 'example_str',
        'exampleInt': 'example_int',
    }

    example_str: str = StringValidator()
    example_int: int = IntegerValidator()

    @classmethod
    def __pre_validate__(cls, input_data: dict) -> dict:
        for from_key, to_key in cls.__key_mapping.items():
            if from_key in input_data:
                input_data[to_key] = input_data.pop(from_key)

        return input_data


@validataclass
class UnitTestPreValidateContextSensitiveDataclass:
    """
    Dataclass with `__pre_validate__()` method that takes named context arguments.

    The context argument `source_field_name` determines the key of the input dictionary that will be mapped to
    `target_field`.
    """
    target_field: int = IntegerValidator()

    @classmethod
    def __pre_validate__(cls, input_data: dict, *, source_field_name: str) -> dict:
        if source_field_name in input_data:
            return {'target_field': input_data[source_field_name]}
        else:
            # Also test raising validation errors in pre-validate here
            raise DictFieldsValidationError(
                field_errors={
                    source_field_name: DictRequiredFieldError(),
                }
            )


@validataclass
class UnitTestPreValidateContextSensitiveVarKwargsDataclass:
    """
    Dataclass with `__pre_validate__()` method that takes variable keyword arguments as context arguments.

    The variable context arguments will be used as default values for the input fields.
    """
    # Note that these fields do not have defined Defaults
    example_str: str = StringValidator()
    example_int: int = IntegerValidator()

    @classmethod
    def __pre_validate__(cls, input_data: dict, **kwargs) -> dict:
        # Fill input_data with default values based on kwargs
        for key, default_value in kwargs.items():
            if key not in input_data:
                input_data[key] = default_value

        return input_data


# Define a bunch of dataclasses with invalid __pre_validate__ method signatures

@validataclass
class UnitTestInvalidPreValidateDataclass1:
    """ Dataclass with invalid __pre_validate__ class method: Not enough arguments. """

    @classmethod
    def __pre_validate__(cls) -> dict:
        return {}


@validataclass
class UnitTestInvalidPreValidateDataclass2:
    """ Dataclass with invalid __pre_validate__ static method: Not enough arguments. """

    @staticmethod
    def __pre_validate__() -> dict:
        return {}


@validataclass
class UnitTestInvalidPreValidateDataclass3:
    """ Dataclass with invalid __pre_validate__ class method: Too many positional arguments. """

    @classmethod
    def __pre_validate__(cls, input_data: dict, _extra_pos_argument) -> dict:
        return input_data


@validataclass
class UnitTestInvalidPreValidateDataclass4:
    """ Dataclass with invalid __pre_validate__ static method: Too many positional arguments. """

    @staticmethod
    def __pre_validate__(input_data: dict, _extra_pos_argument) -> dict:
        return input_data


@validataclass
class UnitTestInvalidPreValidateDataclass5:
    """ Dataclass with invalid __pre_validate__ class method: Too many (variable) positional arguments. """

    @classmethod
    def __pre_validate__(cls, input_data: dict, *_args) -> dict:
        return input_data


@validataclass
class UnitTestInvalidPreValidateDataclass6:
    """ Dataclass with invalid __pre_validate__ static method: Too many (variable) positional arguments. """

    @staticmethod
    def __pre_validate__(input_data: dict, *_args) -> dict:
        return input_data


# Regex-escaped text of exceptions when using __pre_validate__ with invalid method signatures
PRE_VALIDATE_INVALID_SIGNATURE_ERROR = \
    r'UnitTestInvalidPreValidateDataclass\d\.__pre_validate__\(\) must have exactly one positional argument'


class DataclassValidatorTest:
    """
    Unit tests for the DataclassValidator.
    """

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
        """
        Test DataclassValidator with a dataclass with all kinds of Default objects (Default, DefaultUnset,
        DefaultFactory).
        """

        def counter():
            """ Function that counts up every time it is called and saves the counter as an attribute of itself. """
            current = getattr(counter, 'current', 0) + 1
            setattr(counter, 'current', current)
            return current

        @validataclass
        class DataclassWithDefaults:
            default_str: str = StringValidator(), Default('example default')
            default_list: List[int] = ListValidator(IntegerValidator()), Default([])
            default_counter: int = IntegerValidator(), DefaultFactory(counter)
            default_unset: OptionalUnset[str] = StringValidator(), DefaultUnset

        validator = DataclassValidator(DataclassWithDefaults)

        # Validate multiple objects to check that the counter actually counts up
        validated_objects = {i: validator.validate({}) for i in (1, 2, 3)}

        for i, validated_data in validated_objects.items():
            assert validated_data.default_str == 'example default'
            assert validated_data.default_list == []
            assert validated_data.default_counter == i
            assert validated_data.default_unset is UnsetValue

        # Verify that the default list was deepcopied
        assert validated_objects[1].default_list is not validated_objects[2].default_list
        assert validated_objects[2].default_list is not validated_objects[3].default_list

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
        """
        Validate dataclasses with non-init fields and a __post_init__() method that raises a
        DataclassPostValidationError.
        """
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
        """
        Validate dataclasses with non-init fields and a __post_init__() method that raises an arbitrary ValidationError.
        """

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
        """
        Validate dataclasses with non-init fields and a __post_init__() method that raises a non-ValidationError
        exception.
        """

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
            (
                {},
                {'name': 'banana'},
                None,
            ),
            (
                {},
                {'name': 'banana', 'value': 13},
                13,
            ),

            # Context argument "value_required"
            (
                {'value_required': False},
                {'name': 'banana'},
                None,
            ),
            (
                {'value_required': False},
                {'name': 'banana', 'value': 13},
                13,
            ),
            (
                {'value_required': True},
                {'name': 'banana', 'value': 13},
                13,
            ),

            # Test that all context arguments are passed to other validators as well
            (
                {'value_required': False, 'foo': 42},
                {'name': 'banana'},
                None,
            ),
        ],
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
        """
        Validate dataclass with a __post_validate__() method that accepts positional arguments, with invalid input.
        """
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
        ],
    )
    def test_dataclass_with_context_sensitive_post_validate_with_var_kwargs(
        validate_kwargs,
        expected_ctx_a,
        expected_ctx_b,
        expected_extra_kwargs,
    ):
        """
        Validate dataclass with a context-sensitive __post_validate__() method that accepts arbitrary keyword arguments.
        """
        validator = DataclassValidator(UnitTestContextSensitiveDataclassWithVarKwargs)
        validated_data = validator.validate({'name': 'unit-test'}, **validate_kwargs)

        assert validated_data.name == f"unit-test / {validate_kwargs}"
        assert validated_data.ctx_a == expected_ctx_a
        assert validated_data.ctx_b == expected_ctx_b
        assert validated_data.extra_kwargs == expected_extra_kwargs

    # Test dataclasses with __pre_validate__() methods (with and without context-sensitive validation)

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_example_str, expected_example_int',
        [
            # Use "correct" field names (no mapping necessary)
            (
                {
                    'example_str': 'foo',
                    'example_int': 42,
                },
                'foo',
                42,
            ),

            # Use camelCase field names (mapped to snake_case)
            (
                {
                    'exampleStr': 'foo',
                    'exampleInt': 42,
                },
                'foo',
                42,
            ),

            # Use both variants of field names (camelCase variant will take precedence)
            (
                {
                    'example_str': 'foo',
                    'exampleStr': 'bar',
                    'exampleInt': 23,
                    'example_int': 42,
                },
                'bar',
                23,
            ),

            # Unknown field names are ignored (like usually)
            (
                {
                    'example_str': 'foo',
                    'exampleInt': 42,
                    'exampleUnknown': 'meow',
                },
                'foo',
                42,
            ),
        ],
    )
    @pytest.mark.parametrize(
        'dataclass_cls',
        [
            UnitTestPreValidateStaticMethodDataclass,
            UnitTestPreValidateClassMethodDataclass,
        ],
    )
    def test_dataclass_with_pre_validate_methods(
        input_data,
        expected_example_str,
        expected_example_int,
        dataclass_cls,
    ):
        """ Validate dataclasses with different __pre_validate__() methods (static and class methods). """
        validator = DataclassValidator(dataclass_cls)
        validated_data = validator.validate(input_data)

        assert validated_data.example_str == expected_example_str
        assert validated_data.example_int == expected_example_int

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_field_errors',
        [
            # Empty dictionary (all fields are required)
            # NOTE: Field names in the validation error are as defined in the dataclass (not mapped back to camelCase)
            (
                {},
                {
                    'example_str': {'code': 'required_field'},
                    'example_int': {'code': 'required_field'},
                },
            ),

            # Use "correct" field names (no mapping necessary) with invalid data types
            (
                {
                    'example_str': 42,
                    'example_int': 'foo',
                },
                {
                    'example_str': {'code': 'invalid_type', 'expected_type': 'str'},
                    'example_int': {'code': 'invalid_type', 'expected_type': 'int'},
                },
            ),

            # Use camelCase field names (mapped to snake_case) with invalid data types
            (
                {
                    'exampleStr': 42,
                    'exampleInt': 'foo',
                },
                {
                    'example_str': {'code': 'invalid_type', 'expected_type': 'str'},
                    'example_int': {'code': 'invalid_type', 'expected_type': 'int'},
                },
            ),
        ],
    )
    @pytest.mark.parametrize(
        'dataclass_cls',
        [
            UnitTestPreValidateStaticMethodDataclass,
            UnitTestPreValidateClassMethodDataclass,
        ],
    )
    def test_dataclass_with_pre_validate_methods_invalid(
        input_data,
        expected_field_errors,
        dataclass_cls,
    ):
        """ Validate dataclasses with different __pre_validate__() methods and invalid input. """
        validator = DataclassValidator(dataclass_cls)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': expected_field_errors,
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, source_field_name, expected_value',
        [
            ({'foo': 42, 'bar': 23}, 'foo', 42),
            ({'foo': 42, 'bar': 23}, 'bar', 23),
        ],
    )
    def test_dataclass_with_context_sensitive_pre_validate(input_data, source_field_name, expected_value):
        """ Validate dataclass with a context-sensitive __pre_validate__() method. """
        validator = DataclassValidator(UnitTestPreValidateContextSensitiveDataclass)
        validated_data = validator.validate(input_data, source_field_name=source_field_name)

        assert validated_data.target_field == expected_value

    @staticmethod
    def test_dataclass_with_context_sensitive_pre_validate_invalid():
        """ Validate dataclass with a context-sensitive __pre_validate__() method with invalid input data. """
        validator = DataclassValidator(UnitTestPreValidateContextSensitiveDataclass)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({'foo': 42, 'bar': 23}, source_field_name='unknown_field')

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'unknown_field': {'code': 'required_field'},
            },
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, validate_kwargs, expected_example_str, expected_example_int',
        [
            # No context arguments: Both fields required
            (
                {'example_str': 'foo', 'example_int': 42},
                {},
                'foo',
                42,
            ),

            # Context arguments set default values (but don't overwrite set values)
            (
                {'example_str': 'foo', 'example_int': 42},
                {'example_str': 'default_str', 'example_int': 1000},
                'foo',
                42,
            ),
            (
                {'example_int': 42},
                {'example_str': 'default_str', 'example_int': 1000},
                'default_str',
                42,
            ),
            (
                {},
                {'example_str': 'default_str', 'example_int': 1000},
                'default_str',
                1000,
            ),

            # Additional keyword arguments for unknown field names shouldn't cause errors (they will just set fields
            # that don't exist in the dataclass, which will be ignored)
            (
                {'example_str': 'foo', 'example_int': 42},
                {'unknown_field': 1234},
                'foo',
                42,
            ),
        ],
    )
    def test_dataclass_with_context_sensitive_pre_validate_with_var_kwargs(
        input_data,
        validate_kwargs,
        expected_example_str,
        expected_example_int,
    ):
        """ Validate dataclass with a __pre_validate__() method that accepts variable keyword arguments. """
        validator = DataclassValidator(UnitTestPreValidateContextSensitiveVarKwargsDataclass)
        validated_data = validator.validate(input_data, **validate_kwargs)

        assert validated_data.example_str == expected_example_str
        assert validated_data.example_int == expected_example_int

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, validate_kwargs, expected_field_errors',
        [
            # No context arguments: Both fields required
            (
                {},
                {},
                {
                    'example_str': {'code': 'required_field'},
                    'example_int': {'code': 'required_field'},
                },
            ),

            # Context argument sets default value (but other field is still required)
            (
                {},
                {'example_str': 'default_str'},
                {
                    'example_int': {'code': 'required_field'},
                },
            ),
        ],
    )
    def test_dataclass_with_context_sensitive_pre_validate_with_var_kwargs_invalid(
        input_data,
        validate_kwargs,
        expected_field_errors,
    ):
        """
        Test dataclass with a __pre_validate__() method that accepts variable keyword arguments with invalid input.
        """
        validator = DataclassValidator(UnitTestPreValidateContextSensitiveVarKwargsDataclass)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate(input_data, **validate_kwargs)

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': expected_field_errors,
        }

    @staticmethod
    @pytest.mark.parametrize(
        'dataclass_cls',
        [
            UnitTestInvalidPreValidateDataclass1,
            UnitTestInvalidPreValidateDataclass2,
            UnitTestInvalidPreValidateDataclass3,
            UnitTestInvalidPreValidateDataclass4,
            UnitTestInvalidPreValidateDataclass5,
            UnitTestInvalidPreValidateDataclass6,
        ],
    )
    def test_dataclass_with_invalid_forms_of_pre_validate(dataclass_cls):
        """ Test error handling for dataclasses with __pre_validate__() methods with an invalid method signature. """
        validator = DataclassValidator(dataclass_cls)

        with pytest.raises(DataclassInvalidPreValidateSignatureException, match=PRE_VALIDATE_INVALID_SIGNATURE_ERROR):
            validator.validate({})

    # Test invalid validator options

    @staticmethod
    def test_invalid_dataclass_validator_without_dataclass():
        """ Test that a DataclassValidator cannot be created without a dataclass. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DataclassValidator()

        assert (
            str(exception_info.value)
            == 'Parameter "dataclass_cls" must be specified (or set as class member in a subclass).'
        )

    @staticmethod
    @pytest.mark.parametrize(
        'dataclass_cls_param',
        [
            # Type that is not a dataclass (anonymous class)
            type('UnitTestClass', (), {}),

            # Instance of a dataclass (but not the class itself)
            UnitTestDataclass(name='bluenana', color='blue', amount=3, weight=Decimal('1.234')),
        ],
    )
    def test_invalid_dataclass_validator_with_invalid_dataclass(dataclass_cls_param):
        """ Test that a DataclassValidator cannot be created with a class that is not a dataclass. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DataclassValidator(dataclass_cls_param)  # noqa

        assert str(exception_info.value) == 'Parameter "dataclass_cls" must be a dataclass type.'

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
            foo: str = field(default='unknown', metadata={
                'validator': StringValidator(),
                'validator_default': 'foobar',
            })

        with pytest.raises(DataclassValidatorFieldException) as exception_info:
            DataclassValidator(IncompatibleDataclass)

        assert str(exception_info.value) == 'Default specified for dataclass field "foo" is not of type "Default".'
