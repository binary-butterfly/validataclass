# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, ValueNotAllowedError, InvalidValidatorOptionException
from wtfjson.validators import AnyOfValidator


class AnyOfValidatorTest:
    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that AnyOfValidator raises an exception for None as value. """
        validator = AnyOfValidator(['foo', 'bar'])
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    # Test AnyOfValidator with a string value list

    @staticmethod
    def test_string_values_valid():
        """ Test AnyOfValidator with string value list with valid input. """
        validator = AnyOfValidator(['red apple', 'green apple', 'strawberry'])
        assert validator.validate('red apple') == 'red apple'
        assert validator.validate('green apple') == 'green apple'
        assert validator.validate('strawberry') == 'strawberry'

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'bananana', 'red'])
    def test_string_values_invalid_value(input_data):
        """ Test AnyOfValidator with string value list with invalid input. """
        validator = AnyOfValidator(['red apple', 'green apple', 'strawberry'])
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'value_not_allowed'}

    @staticmethod
    @pytest.mark.parametrize('input_data', [1, 1.234, True, ['red apple']])
    def test_string_values_invalid_type(input_data):
        """ Check that AnyOfValidator with string value list raises an exception for values with wrong type. """
        validator = AnyOfValidator(['red apple', 'green apple', 'strawberry'])
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    # Test AnyOfValidator with a integer value list

    @staticmethod
    def test_integer_values_valid():
        """ Test AnyOfValidator with integer value list with valid input. """
        validator = AnyOfValidator([0, 1, -2, 42])
        assert validator.validate(0) == 0
        assert validator.validate(1) == 1
        assert validator.validate(-2) == -2
        assert validator.validate(42) == 42

    @staticmethod
    @pytest.mark.parametrize('input_data', [0, 2, 13])
    def test_integer_values_invalid_value(input_data):
        """ Test AnyOfValidator with integer value list with invalid input. """
        validator = AnyOfValidator([1, -2, 42])
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'value_not_allowed'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', 1.234, True, [1]])
    def test_integer_values_invalid_type(input_data):
        """ Check that AnyOfValidator with integer value list raises an exception for values with wrong type. """
        validator = AnyOfValidator([0, 1, -2, 42])
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'int',
        }

    # Test AnyOfValidator with a mixed type value list

    @staticmethod
    def test_mixed_values_valid():
        """ Test AnyOfValidator with mixed value list with valid input. """
        validator = AnyOfValidator(['strawberry', 42, None])
        assert validator.validate('strawberry') == 'strawberry'
        assert validator.validate(42) == 42
        assert validator.validate(None) is None

    @staticmethod
    @pytest.mark.parametrize('input_data', [0, 13, '', 'banana'])
    def test_mixed_values_invalid_value(input_data):
        """ Test AnyOfValidator with mixed value list with invalid input. """
        validator = AnyOfValidator(['strawberry', 42, None])
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'value_not_allowed'}

    @staticmethod
    @pytest.mark.parametrize('input_data', [1.234, True, False, [1], ['strawberry']])
    def test_mixed_values_invalid_type(input_data):
        """ Check that AnyOfValidator with mixed value list raises an exception for values with wrong type. """
        validator = AnyOfValidator(['strawberry', 42, None])
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['none', 'str', 'int'],
        }

    # Test AnyOfValidator with explicit allowed_types parameter

    @staticmethod
    @pytest.mark.parametrize(
        'allowed_types, expected_type_dict, valid_input_list, invalid_input_list', [
            # Single allowed type
            (str, {'expected_type': 'str'}, ['foo'], [42, 1.234, True]),
            (int, {'expected_type': 'int'}, [42], ['foo', 1.234, True]),
            (float, {'expected_type': 'float'}, [1.234], ['foo', 42, True]),
            # List of types
            ([int], {'expected_type': 'int'}, [42], ['foo', 1.234, True]),
            ([int, float], {'expected_types': ['int', 'float']}, [42, 1.234], ['foo', True]),
        ]
    )
    def test_with_specified_allowed_type(allowed_types, expected_type_dict, valid_input_list, invalid_input_list):
        """ Test AnyOfValidator with mixed value list but restricted allowed types via parameter. """
        validator = AnyOfValidator(['foo', 42, 1.234], allowed_types=allowed_types)

        # Check that allowed types are accepted
        for valid_input in valid_input_list:
            assert validator.validate(valid_input) == valid_input

        # Check that invalid types raise a ValidationError
        for invalid_input in invalid_input_list:
            with pytest.raises(InvalidTypeError) as exception_info:
                validator.validate(invalid_input)
            assert exception_info.value.to_dict() == {
                'code': 'invalid_type',
                **expected_type_dict,
            }

    # Invalid validator parameters

    @staticmethod
    def test_empty_allowed_types():
        """ Check that AnyOfValidator raises exception when allowed_types is empty. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            AnyOfValidator([1, 2, 3], allowed_types=[])
        assert str(exception_info.value) == 'Parameter "allowed_types" is an empty list (or types could not be autodetermined).'
