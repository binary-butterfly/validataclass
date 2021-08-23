# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, NumberRangeError, InvalidValidatorOptionException, \
    NonFiniteNumberError
from wtfjson.validators import FloatValidator


class FloatValidatorTest:
    @staticmethod
    def test_valid_float():
        """ Test FloatValidator with valid floats. """
        validator = FloatValidator()
        assert validator.validate(0.0) == 0.0
        assert validator.validate(1.234) == 1.234
        assert validator.validate(-123.4) == -123.4

    @staticmethod
    def test_invalid_none():
        """ Check that FloatValidator raises exception for None as value. """
        validator = FloatValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', '1.234', True, [1.234]])
    def test_invalid_wrong_type(input_data):
        """ Check that FloatValidator raises exceptions for values that are not of type 'float'. """
        validator = FloatValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'float',
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', [float('infinity'), float('-infinity'), float('nan')])
    def test_invalid_non_finite_numbers(input_data):
        """ Test FloatValidator with non-finite values (infinity, NaN). """
        validator = FloatValidator()
        with pytest.raises(NonFiniteNumberError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'not_a_finite_number'}

    # Test value range requirements

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list', [
            # min_value only
            (0, None, [0.0, 0.1, 123.456]),
            (10.5, None, [10.5, 10.6, 123.456]),
            # max_value only
            (None, 10.0, [-999.0, -1.0, 0.0, 9.9, 10.0]),
            (None, -10.0, [-999.0, -11.0, -10.1, -10.0]),
            # min_value and max_value
            (0, 1, [0.0, 0.001, 0.5, 0.999, 1.0]),
            (-0.5, 0.5, [-0.5, -0.499, -0.1, 0.0, 0.1, 0.499, 0.5]),
        ]
    )
    def test_float_value_range_valid(min_value, max_value, input_data_list):
        """ Test FloatValidator with range requirements with a list of valid floats. """
        validator = FloatValidator(min_value=min_value, max_value=max_value)

        for input_data in input_data_list:
            output_value = validator.validate(input_data)
            assert type(output_value) is float
            assert output_value == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list', [
            # min_value only
            (0, None, [-0.001, -0.1, -123.456]),
            (10.5, None, [10.499, 10.4, 0.0, -10.5, -10.6, -123.456]),
            # max_value only
            (None, 10.0, [10.001, 11.0, 999.0]),
            (None, -10.0, [-9.999, -1.0, 0.0, 9.9, 10.0, 999.0]),
            # min_value and max_value
            (0, 1, [-999.0, -1.0, -0.001, 1.001, 1.1, 999.999]),
            (-0.5, 0.5, [-1.0, -0.6, -0.501, 0.501, 0.6, 1.0]),
        ]
    )
    def test_float_value_range_invalid(min_value, max_value, input_data_list):
        """ Test FloatValidator with range requirements with a list of invalid floats. """
        validator = FloatValidator(min_value=min_value, max_value=max_value)

        # Construct error dict with min_value and/or max_value, depending on which is specified
        expected_error_dict = {'code': 'number_range_error'}
        expected_error_dict.update({'min_value': float(min_value)} if min_value is not None else {})
        expected_error_dict.update({'max_value': float(max_value)} if max_value is not None else {})

        for input_data in input_data_list:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_data)
            assert exception_info.value.to_dict() == expected_error_dict

    # Invalid validator parameters

    @staticmethod
    def test_min_value_greater_than_max_value():
        """ Check that FloatValidator raises exception when min_value is greater than max_value. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            FloatValidator(min_value=1.0, max_value=0.9)
        assert str(exception_info.value) == 'Parameter "min_value" cannot be greater than "max_value".'
