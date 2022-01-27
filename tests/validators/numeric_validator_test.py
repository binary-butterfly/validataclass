"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal

import pytest

from tests.test_utils import unpack_params
from validataclass.exceptions import RequiredValueError, InvalidTypeError, InvalidDecimalError, NumberRangeError, \
    NonFiniteNumberError, InvalidValidatorOptionException
from validataclass.validators import NumericValidator


class NumericValidatorTest:
    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_str', [
            # Integers (shouldn't have trailing '.0' in the output)
            (0, '0'),
            (42, '42'),
            (-123, '-123'),

            # Floats
            (0.0, '0.0'),
            (0.001, '0.001'),
            (1.234, '1.234'),
            (-123.4, '-123.4'),
            (-123456.789, '-123456.789'),

            # Decimal strings
            ('0', '0'),
            ('0.0', '0.0'),
            ('123', '123'),
            ('123.0', '123.0'),
            ('-1.23456', '-1.23456'),
            ('+.001', '0.001'),
        ]
    )
    def test_valid_input(input_data, expected_decimal_str):
        """ Test NumericValidator with valid input data. """
        validator = NumericValidator()
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert str(decimal) == expected_decimal_str

    @staticmethod
    def test_invalid_none():
        """ Check that NumericValidator raises exception for None as value. """
        validator = NumericValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', [True, False, [1.234]])
    def test_invalid_wrong_type(input_data):
        """ Check that NumericValidator raises exceptions for values that are neither of the types float, int and str. """
        validator = NumericValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['float', 'int', 'str'],
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'banana', '1234x', '$123', '1,234', 'Infinity', 'NaN', '.', '1e3'])
    def test_invalid_decimal_strings(input_data):
        """ Test that NumericValidator raises exceptions for invalid or malformed strings. """
        validator = NumericValidator()
        with pytest.raises(InvalidDecimalError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_decimal',
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', [float('infinity'), float('-infinity'), float('nan')])
    def test_invalid_non_finite_numbers(input_data):
        """ Test NumericValidator with non-finite values (infinity, NaN). """
        validator = NumericValidator()
        with pytest.raises(NonFiniteNumberError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'not_a_finite_number'}

    # Test value range requirements

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data, expected_decimal_str', [
            # min_value only (as integer)
            *unpack_params(
                1, None,
                [
                    (1, '1'),
                    (1.0, '1.0'),
                    ('1.000', '1.000'),
                    (999999, '999999'),
                    (999999.999, '999999.999'),
                    ('999999', '999999'),
                ],
            ),

            # max_value only (as float)
            *unpack_params(
                None, 10.0,
                [
                    (-9999, '-9999'),
                    (-9999.0, '-9999.0'),
                    ('-9999.999', '-9999.999'),
                    (10, '10'),
                    (10.0, '10.0'),
                    ('10.0', '10.0'),
                ],
            ),

            # min_value and max_value (as strings)
            *unpack_params(
                '0', '1',
                [
                    (0, '0'),
                    (0.0, '0.0'),
                    ('0.000', '0.000'),
                    (0.001, '0.001'),
                    ('0.999', '0.999'),
                    (1, '1'),
                    (1.0, '1.0'),
                    ('1.000', '1.000'),
                ],
            ),

            # min_value and max_value (as Decimal)
            *unpack_params(
                Decimal('-0.5'), Decimal('0.5'),
                [
                    (-0.5, '-0.5'),
                    ('-0.5', '-0.5'),
                    (0, '0'),
                    (0.1, '0.1'),
                    ('0.499', '0.499'),
                    (0.5, '0.5'),
                    ('0.500', '0.500'),
                ],
            ),
        ]
    )
    def test_value_range_valid(min_value, max_value, input_data, expected_decimal_str):
        """ Test NumericValidator with different range requirements and different types of input values. """
        validator = NumericValidator(min_value=min_value, max_value=max_value)
        output_value = validator.validate(input_data)
        assert type(output_value) is Decimal
        assert str(output_value) == expected_decimal_str

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data', [
            # min_value only (as integer)
            *unpack_params(
                1, None,
                [
                    -1,
                    '-1.0',
                    0,
                    '0.0',
                    0.999,
                    '0.99999'
                ],
            ),

            # max_value only (as float)
            *unpack_params(
                None, 10.0,
                [
                    10.001,
                    '10.001',
                    11,
                    12.345,
                    '999.9',
                ],
            ),

            # min_value and max_value (as strings)
            *unpack_params(
                '0', '1',
                [
                    -1,
                    -0.001,
                    '-0.000001',
                    1.001,
                    '1.000001',
                    2,
                ],
            ),

            # min_value and max_value (as Decimal)
            *unpack_params(
                Decimal('-0.5'), Decimal('0.5'),
                [
                    -1,
                    -0.6,
                    '-0.500001',
                    0.500001,
                    '0.6',
                    1,
                ],
            ),
        ]
    )
    def test_value_range_invalid(min_value, max_value, input_data):
        """ Test NumericValidator with range requirements with invalid input values. """
        validator = NumericValidator(min_value=min_value, max_value=max_value)

        with pytest.raises(NumberRangeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'number_range_error',
            **({'min_value': str(min_value)} if min_value is not None else {}),
            **({'max_value': str(max_value)} if max_value is not None else {}),
        }

    # Test output_places parameter

    @staticmethod
    @pytest.mark.parametrize(
        'output_places, input_data, expected_decimal_str', [
            # output_places=0
            (0, 0.0, '0'),
            (0, -42.0, '-42'),
            (0, 42.0, '42'),
            (0, 123.456, '123'),  # rounded down
            (0, 123.567, '124'),  # rounded up
            # output_places=2
            (2, 0.0, '0.00'),
            (2, -42.0, '-42.00'),
            (2, 42.0, '42.00'),
            (2, 123.454, '123.45'),  # rounded down
            (2, 123.455, '123.46'),  # rounded up
        ]
    )
    def test_output_places(output_places, input_data, expected_decimal_str):
        """ Test NumericValidator with output_places parameter (fixed number of decimal places in output value). """
        validator = NumericValidator(output_places=output_places)
        assert str(validator.validate(input_data)) == expected_decimal_str

    # Invalid validator parameters

    @staticmethod
    def test_min_value_greater_than_max_value():
        """ Check that NumericValidator raises exception when min_value is greater than max_value. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            NumericValidator(min_value=2, max_value=1.9)
        assert str(exception_info.value) == 'Parameter "min_value" cannot be greater than "max_value".'

    @staticmethod
    def test_output_places_negative():
        """ Check that NumericValidator raises exception when output_places is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            NumericValidator(output_places=-1)
        assert str(exception_info.value) == 'Parameter "output_places" cannot be negative.'
