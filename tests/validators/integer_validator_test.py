"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from tests.test_utils import UNSET_PARAMETER
from validataclass.exceptions import RequiredValueError, InvalidTypeError, NumberRangeError, InvalidIntegerError, \
    InvalidValidatorOptionException
from validataclass.validators import IntegerValidator


class IntegerValidatorTest:
    """
    Unit tests for IntegerValidator.
    """

    # General tests

    @staticmethod
    def test_valid_integer():
        """ Test default IntegerValidator with valid integers. """
        validator = IntegerValidator()
        assert validator.validate(0) == 0
        assert validator.validate(123) == 123
        assert validator.validate(-456) == -456

    @staticmethod
    def test_invalid_none():
        """ Check that IntegerValidator raises exceptions for None as value. """
        validator = IntegerValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', '1234', 1.234, True])
    def test_invalid_wrong_type(input_data):
        """ Check that IntegerValidator raises exceptions for values that are not of type 'int'. """
        validator = IntegerValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'int',
        }

    # Tests with and without value range requirements

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list',
        [
            # Use default min_value and max_value (allows 32 bit integers only)
            (UNSET_PARAMETER, UNSET_PARAMETER, [-2147483648, -1, 0, 123, 2147483647]),

            # Only set min_value, use default max_value
            (-1000000000000000, UNSET_PARAMETER, [-1000000000000000, -2147483648, 0, 2147483647]),

            # Only set max_value, use default min_value
            (UNSET_PARAMETER, 1000000000000000, [-2147483648, 0, 2147483647, 1000000000000000]),

            # No limits at all
            (None, None, [-9999999999999999, -2147483648, -1, 0, 123, 2147483647, 9999999999999999]),

            # min_value only
            (2, None, [2, 3, 2147483647, 9999999999999999]),
            (-3, None, [-3, -2, -1, 0, 1, 2147483647, 9999999999999999]),
            (-1000000000000000, None, [-1000000000000000, -2147483648, 9999999999999999]),

            # max_value only
            (None, 10, [-9999999999999999, -2147483648, -1, 0, 9, 10]),
            (None, -10, [-9999999999999999, -2147483648, -11, -10]),
            (None, 1000000000000000, [-9999999999999999, 2147483647, 1000000000000000]),

            # min_value and max_value
            (0, 10, [0, 1, 2, 9, 10]),
            (-10, -1, [-10, -9, -2, -1]),
            (-2, 2, [-2, -1, 0, 1, 2]),
            (1, 1, [1]),
        ]
    )
    def test_integer_value_range_valid(min_value, max_value, input_data_list):
        """ Test IntegerValidator with range requirements with a list of valid integers. """
        # Set validator parameters (use defaults if unset)
        validator_args = {}
        if min_value is not UNSET_PARAMETER:
            validator_args['min_value'] = min_value
        if max_value is not UNSET_PARAMETER:
            validator_args['max_value'] = max_value

        validator = IntegerValidator(**validator_args)

        # Test validator for every integer in the list
        for input_data in input_data_list:
            assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list',
        [
            # Use default min_value and max_value (allows 32 bit integers only)
            (UNSET_PARAMETER, UNSET_PARAMETER, [-1000000000000000, -2147483649, 2147483648, 1000000000000000]),

            # Only set min_value, use default max_value
            (-1000000000000000, UNSET_PARAMETER, [-1000000000000001, 2147483648, 1000000000000000]),

            # Only set max_value, use default min_value
            (UNSET_PARAMETER, 1000000000000000, [-1000000000000000, -2147483649, 1000000000000001]),

            # min_value only
            (2, None, [-99999999999, -2147483648, -1, 0, 1]),
            (-3, None, [-99999999999, -2147483648, -5, -4]),
            (-1000000000000000, None, [-1000000000000001]),

            # max_value only
            (None, 10, [11, 12, 2147483647, 99999999999]),
            (None, -10, [-9, 0, 9, 10, 2147483647, 99999999999]),
            (None, 1000000000000000, [1000000000000001]),

            # min_value and max_value
            (0, 10, [-99999999999, -2147483648, -2, -1, 11, 12, 2147483647, 99999999999]),
            (-10, -1, [-11, 0, 1, 10]),
            (-2, 2, [-4, -3, 3, 4]),
            (1, 1, [-1, 0, 2]),
        ]
    )
    def test_integer_value_range_invalid(min_value, max_value, input_data_list):
        """ Test IntegerValidator with range requirements with a list of invalid integers. """
        # Set validator parameters (use defaults if unset)
        validator_args = {}
        if min_value is not UNSET_PARAMETER:
            validator_args['min_value'] = min_value
        if max_value is not UNSET_PARAMETER:
            validator_args['max_value'] = max_value

        validator = IntegerValidator(**validator_args)

        # Construct error dict with min_value and/or max_value, depending on which is specified
        expected_error_dict = {'code': 'number_range_error'}
        if min_value is not None:
            expected_error_dict['min_value'] = min_value if min_value is not UNSET_PARAMETER else -2147483648
        if max_value is not None:
            expected_error_dict['max_value'] = max_value if max_value is not UNSET_PARAMETER else 2147483647

        # Test validator for every integer in the list
        for input_data in input_data_list:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_data)
            assert exception_info.value.to_dict() == expected_error_dict

    # Test optional allow_strings parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_output',
        [
            # Actual integers should still work of course
            (0, 0),
            (42, 42),
            (-123, -123),

            # Integers as strings
            ('0', 0),
            ('42', 42),
            ('-123', -123),
            ('2147483647', 2147483647),
            ('-2147483648', -2147483648),
        ]
    )
    def test_allow_strings_valid(input_data, expected_output):
        """ Test IntegerValidator with allow_strings=True with valid input (both as integers and strings). """
        validator = IntegerValidator(allow_strings=True)
        output = validator.validate(input_data)
        assert type(output) is int
        assert output == expected_output

    @staticmethod
    def test_allow_strings_with_invalid_type():
        """ Test that IntegerValidator with allow_strings=True only accepts integers and strings. """
        validator = IntegerValidator(allow_strings=True)
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(1.234)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['int', 'str'],
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'banana', '1.234', 'NaN', 'Infinity', '1e3'])
    def test_allow_strings_with_invalid_strings(input_data):
        """ Test that IntegerValidator with allow_strings=True raises exceptions on invalid (non-numeric) strings as input. """
        validator = IntegerValidator(allow_strings=True)

        with pytest.raises(InvalidIntegerError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_integer',
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', ['-999999999999', '-2147483649', '2147483648', '999999999999'])
    def test_allow_strings_with_default_value_range_invalid(input_data):
        """
        Test that IntegerValidator with allow_strings=True and default min_value/max_value raises exceptions for integers
        outside these values (i.e. integers not fitting into 32 bits).
        """
        validator = IntegerValidator(allow_strings=True)

        with pytest.raises(NumberRangeError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {
            'code': 'number_range_error',
            'min_value': IntegerValidator.DEFAULT_MIN_VALUE,
            'max_value': IntegerValidator.DEFAULT_MAX_VALUE,
        }

    @staticmethod
    def test_allow_strings_without_value_range():
        """ Test IntegerValidation with allow_strings=True and with min_value=None, max_value=None. """
        validator = IntegerValidator(min_value=None, max_value=None, allow_strings=True)

        # Valid input
        assert validator.validate('0') == 0
        assert validator.validate('-99999999999999') == -99999999999999
        assert validator.validate('99999999999999') == 99999999999999

    @staticmethod
    def test_allow_strings_with_value_range():
        """ Test IntegerValidation with allow_strings=True and a value range. """
        validator = IntegerValidator(min_value=-5, max_value=10, allow_strings=True)

        # Valid input
        assert validator.validate('-5') == -5
        assert validator.validate('10') == 10

        # Invalid input
        for input_value in ['-6', '11']:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_value)
            assert exception_info.value.to_dict() == {
                'code': 'number_range_error',
                'min_value': -5,
                'max_value': 10,
            }

    # Invalid validator parameters

    @staticmethod
    def test_min_value_greater_than_max_value():
        """ Check that IntegerValidator raises exception when min_value is greater than max_value. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            IntegerValidator(min_value=4, max_value=3)
        assert str(exception_info.value) == 'Parameter "min_value" cannot be greater than "max_value".'
