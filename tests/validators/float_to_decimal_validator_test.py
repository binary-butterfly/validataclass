# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, NumberRangeError, NonFiniteNumberError, \
    InvalidValidatorOptionException
from wtfjson.validators import FloatToDecimalValidator


class FloatToDecimalValidatorTest:
    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_string', [
            (0.0, '0'),
            (1.234, '1.234'),
            (-0.001, '-0.001'),
            (-123456.789, '-123456.789'),
        ]
    )
    def test_valid_float(input_data, expected_decimal_string):
        """ Test FloatToDecimalValidator with valid floats. """
        validator = FloatToDecimalValidator()
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert decimal == Decimal(expected_decimal_string)

    @staticmethod
    def test_invalid_none():
        """ Check that FloatToDecimalValidator raises exception for None as value. """
        validator = FloatToDecimalValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', '1.234', True, [1.234]])
    def test_invalid_wrong_type(input_data):
        """ Check that FloatToDecimalValidator raises exceptions for values that are not of type 'float'. """
        validator = FloatToDecimalValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'float',
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', [float('infinity'), float('-infinity'), float('nan')])
    def test_invalid_non_finite_numbers(input_data):
        """ Test FloatToDecimalValidator with non-finite values (infinity, NaN). """
        validator = FloatToDecimalValidator()
        with pytest.raises(NonFiniteNumberError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'not_a_finite_number'}

    # Test value range requirements

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data, expected_decimal_string', [
            # min_value only
            (3.0, None, 3.0, '3.0'),
            (3.0, None, 3.1, '3.1'),
            # max_value only
            (None, 10.0, -999.0, '-999.0'),
            (None, 10.0, 9.9, '9.9'),
            (None, 10.0, 10.0, '10.0'),
            # min_value and max_value
            (0, 1, 0.0, '0.0'),
            (0, 1, 0.9, '0.9'),
            (0, 1, 1.0, '1.0'),
        ]
    )
    def test_float_value_range_valid(min_value, max_value, input_data, expected_decimal_string):
        """ Test FloatToDecimalValidator with range requirements with a list of valid floats. """
        validator = FloatToDecimalValidator(min_value=min_value, max_value=max_value)
        output_value = validator.validate(input_data)

        assert type(output_value) is Decimal
        assert output_value == Decimal(expected_decimal_string)

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data_list', [
            # min_value only
            (3.0, None, [2.999, 2.9, -3.0]),
            # max_value only
            (None, 10.0, [10.001, 11.0, 999.0]),
            # min_value and max_value
            (0, 1, [-1.0, -0.001, 1.001, 1.1]),
        ]
    )
    def test_float_value_range_invalid(min_value, max_value, input_data_list):
        """ Test FloatToDecimalValidator with range requirements with a list of invalid floats. """
        validator = FloatToDecimalValidator(min_value=min_value, max_value=max_value)

        # Construct error dict with min_value and/or max_value, depending on which is specified
        expected_error_dict = {'code': 'number_range_error'}
        expected_error_dict.update({'max_value': float(max_value)} if max_value is not None else {})
        expected_error_dict.update({'min_value': float(min_value)} if min_value is not None else {})

        for input_data in input_data_list:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_data)
            assert exception_info.value.to_dict() == expected_error_dict

    # Test output_places parameter

    @staticmethod
    @pytest.mark.parametrize(
        'output_places, input_data, expected_output', [
            # output_places=0
            (0, 0.0, '0'),
            (0, -42.0, '-42'),
            (0, 42.0, '42'),
            (0, 123.456, '123'),  # rounded down
            (0, 123.567, '124'),  # rounded up
            # output_places=3
            (3, 0.0, '0.000'),
            (3, -42.0, '-42.000'),
            (3, 42.0, '42.000'),
            (3, 123.456, '123.456'),
            (3, 123.456789, '123.457'),
        ]
    )
    def test_output_places(output_places, input_data, expected_output):
        """ Test FloatToDecimalValidator with output_places parameter (fixed number of decimal places in output value). """
        validator = FloatToDecimalValidator(output_places=output_places)
        assert validator.validate(input_data) == Decimal(expected_output)

    # Invalid validator parameters

    @staticmethod
    def test_min_value_greater_than_max_value():
        """ Check that FloatToDecimalValidator raises exception when min_value is greater than max_value. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            FloatToDecimalValidator(min_value=1.0, max_value=0.9)
        assert str(exception_info.value) == 'Parameter "min_value" cannot be greater than "max_value".'

    @staticmethod
    def test_output_places_negative():
        """ Check that FloatToDecimalValidator raises exception when output_places is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            FloatToDecimalValidator(output_places=-1)
        assert str(exception_info.value) == 'Parameter "output_places" cannot be negative.'
