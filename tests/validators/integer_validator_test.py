# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, NumberRangeError, InvalidValidatorOptionException
from wtfjson.validators import IntegerValidator


class IntegerValidatorTest:
    @staticmethod
    def test_valid_integer():
        """ Test IntegerValidator with valid integers. """
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

    # Test value range requirement check

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list', [
            # min_value only
            (2, None, [2, 3, 99999]),
            (-3, None, [-3, -2, -1, 0, 1, 99999]),
            # max_value only
            (None, 10, [-99999, -1, 0, 9, 10]),
            (None, -10, [-99999, -11, -10]),
            # min_value and max_value
            (0, 10, [0, 1, 2, 9, 10]),
            (-10, -1, [-10, -9, -2, -1]),
            (-2, 2, [-2, -1, 0, 1, 2]),
            (1, 1, [1]),
        ]
    )
    def test_integer_value_range_valid(min_value, max_value, input_data_list):
        """ Test IntegerValidator with range requirements with a list of valid integers. """
        validator = IntegerValidator(min_value=min_value, max_value=max_value)
        for input_data in input_data_list:
            assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list', [
            # min_value only
            (2, None, [-2, -1, 0, 1]),
            (-3, None, [-5, -4]),
            # max_value only
            (None, 10, [11, 12]),
            (None, -10, [-9, 0, 9, 10, 11]),
            # min_value and max_value
            (0, 10, [-2, -1, 11, 12]),
            (-10, -1, [-11, 0, 1, 10]),
            (-2, 2, [-4, -3, 3, 4]),
            (1, 1, [-1, 0, 2]),
        ]
    )
    def test_integer_value_range_invalid(min_value, max_value, input_data_list):
        """ Test IntegerValidator with range requirements with a list of invalid integers. """
        validator = IntegerValidator(min_value=min_value, max_value=max_value)

        # Construct error dict with min_value and/or max_value, depending on which is specified
        expected_error_dict = {'code': 'number_range_error'}
        expected_error_dict.update({'min_value': min_value} if min_value is not None else {})
        expected_error_dict.update({'max_value': max_value} if max_value is not None else {})

        for input_data in input_data_list:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_data)
            assert exception_info.value.to_dict() == expected_error_dict

    # Invalid validator parameters

    @staticmethod
    def test_min_value_greater_than_max_value():
        """ Check that IntegerValidator raises exception when min_value is greater than max_value. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            IntegerValidator(min_value=4, max_value=3)
        assert str(exception_info.value) == 'Parameter "min_value" cannot be greater than "max_value".'
