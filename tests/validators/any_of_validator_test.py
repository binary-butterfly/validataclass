"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import RequiredValueError, InvalidTypeError, ValueNotAllowedError, InvalidValidatorOptionException
from validataclass.validators import AnyOfValidator


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
    @pytest.mark.parametrize('input_data', ['', 'bananana', 'red', 'STRAWBERRY'])
    def test_string_values_invalid_value(input_data):
        """ Test AnyOfValidator with string value list with invalid input. """
        validator = AnyOfValidator(['red apple', 'green apple', 'strawberry'])
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'value_not_allowed',
            'allowed_values': ['red apple', 'green apple', 'strawberry'],
        }

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

    # Test AnyOfValidator with a set of integer values

    @staticmethod
    def test_integer_values_valid():
        """ Test AnyOfValidator with integer value list with valid input. """
        validator = AnyOfValidator({0, 1, -2, 42})
        assert validator.validate(0) == 0
        assert validator.validate(1) == 1
        assert validator.validate(-2) == -2
        assert validator.validate(42) == 42

    @staticmethod
    @pytest.mark.parametrize('input_data', [0, 2, 13])
    def test_integer_values_invalid_value(input_data):
        """ Test AnyOfValidator with integer value list with invalid input. """
        validator = AnyOfValidator({1, -2, 42})
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)

        # Sets are unordered, so checking the exception dictionary is a bit more annoying here
        exception_dict = exception_info.value.to_dict()
        assert exception_dict['code'] == 'value_not_allowed'
        assert sorted(exception_dict['allowed_values']) == [-2, 1, 42]

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', 1.234, True, [1]])
    def test_integer_values_invalid_type(input_data):
        """ Check that AnyOfValidator with integer value list raises an exception for values with wrong type. """
        validator = AnyOfValidator({0, 1, -2, 42})
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'int',
        }

    # Test AnyOfValidator with allowed values of mixed types as a tuple

    @staticmethod
    def test_mixed_values_valid():
        """ Test AnyOfValidator with allowed values of mixed types with valid input. """
        validator = AnyOfValidator(allowed_values=('strawberry', 42, None))
        assert validator.validate('strawberry') == 'strawberry'
        assert validator.validate(42) == 42
        assert validator.validate(None) is None

    @staticmethod
    @pytest.mark.parametrize('input_data', [0, 13, '', 'banana', 'STRAWBERRY'])
    def test_mixed_values_invalid_value(input_data):
        """ Test AnyOfValidator with allowed values of mixed types with invalid input. """
        validator = AnyOfValidator(allowed_values=('strawberry', 42, None))
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'value_not_allowed',
            'allowed_values': ['strawberry', 42, None],
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', [1.234, True, False, [1], ['strawberry']])
    def test_mixed_values_invalid_type(input_data):
        """ Check that AnyOfValidator with allowed values of mixed types raises an exception for values with wrong type. """
        validator = AnyOfValidator(allowed_values=('strawberry', 42, None))
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['int', 'none', 'str'],
        }

    @staticmethod
    @pytest.mark.parametrize(
        'value_list, invalid_input', [
            ([123, True], 1),
            ([123, False], 0),
            ([0, True], False),
            ([1, False], True),
        ]
    )
    def test_mixed_values_typesafety(value_list, invalid_input):
        """ Check that AnyOfValidator with mixed value lists containing booleans and integers are typesafe. """
        validator = AnyOfValidator(value_list)

        # Ensure that all values in the value list are accepted by the validator
        for valid_input in value_list:
            assert validator.validate(valid_input) == valid_input

        # Check against "false positives" (e.g. don't confuse integer 1 with boolean True, or 0 with False)
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(invalid_input)
        assert exception_info.value.to_dict() == {
            'code': 'value_not_allowed',
            'allowed_values': value_list,
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
            ([int, float], {'expected_types': ['float', 'int']}, [42, 1.234], ['foo', True]),
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

    # Test AnyOfValidator with case-insensitive option

    @staticmethod
    @pytest.mark.parametrize(
        'case_insensitive, input_data, expected_result',
        [
            # Case-sensitive matching
            (False, 'Strawberry', 'Strawberry'),
            (False, 42, 42),

            # Case-insensitive matching
            (True, 'Strawberry', 'Strawberry'),
            (True, 'STRAWBERRY', 'Strawberry'),
            (True, 'strawberry', 'Strawberry'),
            (True, 42, 42),
        ]
    )
    def test_case_insensitive_valid(case_insensitive, input_data, expected_result):
        """ Test AnyOfValidator with case-sensitive and case-insensitive string matching, valid input. """
        validator = AnyOfValidator(allowed_values=['Strawberry', 42], case_insensitive=case_insensitive)
        assert validator.validate(input_data) == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        'case_insensitive, input_data',
        [
            # Case-sensitive matching
            (False, 'strawberry'),
            (False, 'banana'),
            (False, 13),

            # Case-insensitive matching
            (True, 'straw_berry'),
            (True, 'banana'),
            (True, 13),
        ]
    )
    def test_case_insensitive_invalid(case_insensitive, input_data):
        """ Test AnyOfValidator with case-sensitive and case-insensitive string matching, invalid input. """
        validator = AnyOfValidator(allowed_values=['Strawberry', 42], case_insensitive=case_insensitive)
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'value_not_allowed',
            'allowed_values': ['Strawberry', 42],
        }

    # Tests for validation errors

    @staticmethod
    def test_value_not_allowed_error_with_too_many_allowed_values():
        """ Test that AnyOfValidator does not include list of allowed values in validation error if too long. """
        validator = AnyOfValidator(allowed_values=range(100))

        # Valid input
        assert validator.validate(0) == 0
        assert validator.validate(99) == 99

        # Invalid input
        with pytest.raises(ValueNotAllowedError) as exception_info:
            validator.validate(100)

        # Validation error should NOT contain "allowed_values"
        assert exception_info.value.to_dict() == {'code': 'value_not_allowed'}

    # Invalid validator parameters

    @staticmethod
    def test_empty_allowed_types():
        """ Check that AnyOfValidator raises exception when allowed_types is empty. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            AnyOfValidator([1, 2, 3], allowed_types=[])
        assert str(exception_info.value) == 'Parameter "allowed_types" is an empty list (or types could not be autodetermined).'
