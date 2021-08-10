# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal

import pytest

from wtfjson.exceptions import DictFieldsValidationError, DictInvalidKeyTypeError, InvalidTypeError, RequiredValueError, \
    InvalidValidatorOptionException

from wtfjson.validators import DictValidator, DecimalValidator, IntegerValidator, StringValidator, Noneable, ListValidator


class DictValidatorTest:
    # Tests for DictValidator only with default_validator (no field_validators)

    @staticmethod
    def test_simple_dict_empty():
        """ Validate a "simple" dictionary without field definitions with empty input. """
        validator = DictValidator(default_validator=IntegerValidator())
        validated_data = validator.validate({})

        assert type(validated_data) is dict
        assert validated_data == {}

    @staticmethod
    def test_simple_dict_invalid_none():
        """ Validate a "simple" dictionary without field definitions with empty input. """
        validator = DictValidator(default_validator=IntegerValidator())
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_simple_dict_valid():
        """ Validate a "simple" dictionary without field definitions with valid input. """
        validator = DictValidator(default_validator=DecimalValidator())
        validated_data = validator.validate({
            'foo': '3.1415',
            'bar': '-0.42',
            'baz': '3',
        })

        assert type(validated_data) is dict
        assert validated_data == {
            'foo': Decimal('3.1415'),
            'bar': Decimal('-0.42'),
            'baz': Decimal('3'),
        }

    @staticmethod
    def test_simple_dict_invalid_fields():
        """ Validate a "simple" dictionary with input data that has invalid fields (that fail the default_validator). """
        validator = DictValidator(default_validator=DecimalValidator())
        with pytest.raises(DictFieldsValidationError) as exception_info:
            # Validate a dict that has one valid field and three invalid fields
            validator.validate({
                'one_valid_field': '3.1415',
                'foo': 'meow',
                # Note: This also tests that fields must not be None
                'bar': None,
                'baz': 123,
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'foo': {'code': 'invalid_decimal'},
                'bar': {'code': 'required_value'},
                'baz': {'code': 'invalid_type', 'expected_type': 'str'},
            },
        }

    @staticmethod
    def test_simple_dict_invalid_not_a_dict():
        """ Validate a dictionary that is not a dictionary, resulting in an InvalidTypeError. """
        validator = DictValidator(default_validator=DecimalValidator())
        with pytest.raises(InvalidTypeError) as exception_info:
            # Try to validate a list as a dictionary
            validator.validate(['1.23', '4.56'])

        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'dict',
        }

    @staticmethod
    def test_simple_dict_with_required_fields_valid():
        """ Validate a simple dictionary that has required keys with valid data. """
        validator = DictValidator(default_validator=DecimalValidator(), required_fields=['foo', 'bar'])
        validated_data = validator.validate({
            'foo': '3.1415',
            'bar': '-0.42',
            'baz': '3',
        })

        assert type(validated_data) is dict
        assert validated_data == {
            'foo': Decimal('3.1415'),
            'bar': Decimal('-0.42'),
            'baz': Decimal('3'),
        }

    @staticmethod
    def test_simple_dict_with_required_fields_missing():
        """ Validate a simple dictionary that has required keys with valid data. """
        validator = DictValidator(default_validator=DecimalValidator(), required_fields=['foo', 'bar', 'baz'])

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'something_else': '1.42',
                'bar': '-0.42',
                'different_error': 'banana',
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'foo': {'code': 'required_field'},
                'baz': {'code': 'required_field'},
                'different_error': {'code': 'invalid_decimal'},
            },
        }

    # Tests for DictValidator with defined field_validators (with and without default_validator)

    @staticmethod
    def test_field_dict_without_default_validator_valid():
        """ Validate a dictionary with defined field validators, all fields required, without default_validator. """
        validator = DictValidator(field_validators={
            'test_int': IntegerValidator(),
            'test_dec': DecimalValidator(),
        })
        validated_data = validator.validate({
            'test_dec': '13.37',
            'test_int': 123,
            # This field should be silently ignored, because no default_validator is defined
            'unknown_field': 'test',
        })

        assert type(validated_data) is dict
        assert validated_data == {
            'test_dec': Decimal('13.37'),
            'test_int': 123,
        }

    @staticmethod
    def test_field_dict_with_missing_required_fields():
        """ Validate a dictionary with defined field validators, all fields required, but missing a field. """
        validator = DictValidator(field_validators={
            'test_int': IntegerValidator(),
            'test_dec': DecimalValidator(),
        })
        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'test_dec': '13.37',
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'test_int': {'code': 'required_field'},
            },
        }

    @staticmethod
    def test_field_dict_with_default_validator_valid():
        """ Validate a dictionary with defined field validators, default validator, all fields required. """
        validator = DictValidator(
            field_validators={
                'test_int': IntegerValidator(),
                'test_dec': DecimalValidator(),
            },
            default_validator=DecimalValidator()
        )
        validated_data = validator.validate({
            'test_dec': '13.37',
            'test_int': 123,
            # This field should now be validated using the default validator
            'unknown_field': '-0.1',
        })

        assert type(validated_data) is dict
        assert validated_data == {
            'test_dec': Decimal('13.37'),
            'test_int': 123,
            'unknown_field': Decimal('-0.1'),
        }

    @staticmethod
    def test_field_dict_with_default_validator_invalid_fields():
        """ Validate a dictionary with defined field validators, default validator, with invalid field values. """
        validator = DictValidator(
            field_validators={
                'test_int': IntegerValidator(),
                'test_dec': DecimalValidator(),
            },
            default_validator=DecimalValidator()
        )
        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'test_dec': '13.37',
                'test_int': 'this should not be a string',
                # This field should now be validated using the default validator
                'unknown_field': 'this is not a valid decimal',
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'test_int': {'code': 'invalid_type', 'expected_type': 'int'},
                'unknown_field': {'code': 'invalid_decimal'},
            },
        }

    # Tests for the required_fields / optional_fields settings (no validation, just checks the internal 'required_fields')

    @staticmethod
    def test_required_fields_without_field_validators_default():
        """ Test that required_fields is empty when defining no field validators. """
        validator = DictValidator(default_validator=IntegerValidator())

        # As no fields are defined, required_fields should be empty
        assert validator.required_fields == set()

    @staticmethod
    def test_required_fields_default():
        """ Test that required_fields is set correctly without specifying required or optional fields. """
        validator = DictValidator(field_validators={
            'a': IntegerValidator(),
            'b': DecimalValidator(),
            'c': StringValidator(),
        })

        # Note: required_fields internally is a set, not a list
        assert validator.required_fields == {'a', 'b', 'c'}

    @staticmethod
    def test_required_fields_set_explicitly():
        """ Test that required_fields is set correctly when specifying it explicitly. """
        validator = DictValidator(
            field_validators={
                'a': IntegerValidator(),
                'b': DecimalValidator(),
                'c': StringValidator(),
            },
            required_fields=['a', 'c']
        )

        # Note: required_fields internally is a set, not a list
        assert validator.required_fields == {'a', 'c'}

    @staticmethod
    def test_required_fields_set_with_optional_fields():
        """ Test that required_fields is set correctly when specifying optional_fields. """
        validator = DictValidator(
            field_validators={
                'a': IntegerValidator(),
                'b': DecimalValidator(),
                'c': StringValidator(),
            },
            optional_fields=['a', 'b']
        )

        # Note: required_fields internally is a set, not a list
        assert validator.required_fields == {'c'}

    @staticmethod
    def test_required_fields_with_all_optional():
        """ Test that required_fields is set correctly when making all fields optional. """
        validator = DictValidator(
            field_validators={
                'a': IntegerValidator(),
                'b': DecimalValidator(),
                'c': StringValidator(),
            },
            required_fields=[]
        )

        # Note: required_fields internally is a set, not a list
        assert validator.required_fields == set()

    # Test DictValidator with a Noneable field

    @staticmethod
    def test_dict_with_noneable_fields():
        """ Validate a dictionary that allows fields with None as value. """
        validator = DictValidator(field_validators={
            'test_a': Noneable(DecimalValidator()),
            'test_b': Noneable(DecimalValidator()),
        })
        validated_data = validator.validate({
            'test_a': '13.37',
            'test_b': None,
        })

        assert type(validated_data) is dict
        assert validated_data == {
            'test_a': Decimal('13.37'),
            'test_b': None,
        }

    # Test invalid validator options

    @staticmethod
    def test_dict_validator_without_validators():
        """ Test that a DictValidator cannot be created without either field_validators or default_validator. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DictValidator()

        assert str(exception_info.value) == \
               "At least one of the parameters 'field_validators' and 'default_validator' needs to be specified."

    @staticmethod
    def test_dict_validator_with_required_fields_and_optional_fields():
        """ Test that a DictValidator cannot be created both required_fields and optional_fields set. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DictValidator(
                field_validators={
                    'a': IntegerValidator(),
                    'b': StringValidator(),
                },
                required_fields=['a'],
                optional_fields=['b']
            )

        assert str(exception_info.value) == "Parameters 'required_fields' and 'optional_fields' cannot be combined."

    # Test DictValidator with invalid keys

    @staticmethod
    def test_dict_with_invalid_keys():
        """ Test that DictValidator only allows strings as keys. """
        validator = DictValidator(default_validator=IntegerValidator())
        with pytest.raises(DictInvalidKeyTypeError) as exception_info:
            validator.validate({
                1: 2,
                3: 4,
            })

        assert exception_info.value.to_dict() == {
            'code': 'dict_invalid_key_type',
        }

    # Test nested DictValidators (and ListValidators in DictValidators)

    @staticmethod
    def test_nested_dicts_valid():
        validator = DictValidator(
            field_validators={
                'fruit': StringValidator(),
                'inner_dict': DictValidator(field_validators={
                    'some_number': IntegerValidator(),
                    'some_decimal': DecimalValidator(),
                }),
                'cool_numbers': ListValidator(DecimalValidator()),
            }
        )

        validated_data = validator.validate({
            'fruit': 'banana',
            'inner_dict': {
                'some_number': 1234,
                'some_decimal': '1.234',
            },
            'cool_numbers': [
                '3.14159',
                '1.41421',
                '2.71828',
            ],
        })

        assert validated_data == {
            'fruit': 'banana',
            'inner_dict': {
                'some_number': 1234,
                'some_decimal': Decimal('1.234'),
            },
            'cool_numbers': [
                Decimal('3.14159'),
                Decimal('1.41421'),
                Decimal('2.71828'),
            ],
        }

    @staticmethod
    def test_nested_dicts_invalid_fields():
        validator = DictValidator(
            field_validators={
                'fruit': StringValidator(),
                'inner_dict': DictValidator(field_validators={
                    'some_number': IntegerValidator(),
                    'some_decimal': DecimalValidator(),
                }),
                'cool_numbers': ListValidator(DecimalValidator()),
            }
        )

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'fruit': 5,
                'inner_dict': {
                    'some_number': 'meow',
                    'some_decimal': 'meow',
                },
                'cool_numbers': [
                    '3.14159',
                    None,
                    10,
                ],
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'fruit': {
                    'code': 'invalid_type',
                    'expected_type': 'str',
                },
                'inner_dict': {
                    'code': 'field_errors',
                    'field_errors': {
                        'some_number': {'code': 'invalid_type', 'expected_type': 'int'},
                        'some_decimal': {'code': 'invalid_decimal'},
                    },
                },
                'cool_numbers': {
                    'code': 'list_item_errors',
                    'item_errors': {
                        1: {'code': 'required_value'},
                        2: {'code': 'invalid_type', 'expected_type': 'str'},
                    },
                },
            },
        }

    # Test subclassing DictValidators

    @staticmethod
    def test_subclassed_dict_valid():
        # TODO: simpler way to subclass dicts (without needing to define __init__)
        class UnitTestNestedDictValidator(DictValidator):
            def __init__(self):
                super().__init__(
                    field_validators={
                        'name': StringValidator(),
                        'value': DecimalValidator(),
                    },
                )

        validator = UnitTestNestedDictValidator()
        validated_data = validator.validate({
            'name': 'pi',
            'value': '3.14159',
        })
        assert validated_data == {
            'name': 'pi',
            'value': Decimal('3.14159'),
        }

    @staticmethod
    def test_subclassed_dict_invalid_fields():
        # TODO: simpler way to subclass dicts (without needing to define __init__)
        class UnitTestNestedDictValidator(DictValidator):
            def __init__(self):
                super().__init__(
                    field_validators={
                        'name': StringValidator(),
                        'value': DecimalValidator(),
                    },
                )

        validator = UnitTestNestedDictValidator()
        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'name': 123,
                'value': 'meow',
            })
        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'name': {'code': 'invalid_type', 'expected_type': 'str'},
                'value': {'code': 'invalid_decimal'},
            },
        }
