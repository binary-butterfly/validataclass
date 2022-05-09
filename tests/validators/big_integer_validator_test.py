"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import RequiredValueError, InvalidTypeError, NumberRangeError
from validataclass.validators import BigIntegerValidator


class BigIntegerValidatorTest:
    """
    Unit tests for BigIntegerValidator.
    """

    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that BigIntegerValidator raises exceptions for None as value. """
        validator = BigIntegerValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', '1234', 1.234, True])
    def test_invalid_wrong_type(input_data):
        """ Check that BigIntegerValidator raises exceptions for values that are not of type 'int'. """
        validator = BigIntegerValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'int',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            -10000000000000000000,
            -2147483648,
            0,
            123,
            2147483647,
            10000000000000000000,
        ]
    )
    def test_without_value_range(input_data):
        """ Test the BigIntegerValidator with the default min_value and max_value (i.e. no limit). """
        validator = BigIntegerValidator()
        assert validator.validate(input_data) == input_data

    # Tests with min_value

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            100,
            2147483647,
            10000000000000000000,
        ]
    )
    def test_with_min_value_valid(input_data):
        """ Test the BigIntegerValidator with the min_value parameter for valid input. """
        validator = BigIntegerValidator(min_value=100)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            -10000000000000000000,
            -2147483648,
            0,
            99,
        ]
    )
    def test_with_min_value_invalid(input_data):
        """ Test the BigIntegerValidator with the min_value parameter for invalid input. """
        validator = BigIntegerValidator(min_value=100)

        with pytest.raises(NumberRangeError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {
            'code': 'number_range_error',
            'min_value': 100,
        }

    # Tests with min_value and max_value

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            100,
            999,
            1000,
        ]
    )
    def test_with_min_and_max_value_valid(input_data):
        """ Test the BigIntegerValidator with min_value and max_value for valid input. """
        validator = BigIntegerValidator(min_value=100, max_value=1000)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            -1000000000000000,
            0,
            99,
            1001,
            1000000000000000,
        ]
    )
    def test_with_min_and_max_value_invalid(input_data):
        """ Test the BigIntegerValidator with min_value and max_value for invalid input. """
        validator = BigIntegerValidator(min_value=100, max_value=1000)

        with pytest.raises(NumberRangeError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {
            'code': 'number_range_error',
            'min_value': 100,
            'max_value': 1000,
        }
