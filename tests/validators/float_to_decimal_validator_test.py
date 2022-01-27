"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal

import pytest

from tests.test_utils import unpack_params
from validataclass.exceptions import RequiredValueError, InvalidTypeError, NumberRangeError, NonFiniteNumberError, \
    InvalidDecimalError, InvalidValidatorOptionException
from validataclass.validators import FloatToDecimalValidator


class FloatToDecimalValidatorTest:
    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_str', [
            (0.0, '0.0'),
            (1.234, '1.234'),
            (-0.001, '-0.001'),
            (-123456.789, '-123456.789'),
        ]
    )
    def test_valid_float(input_data, expected_decimal_str):
        """ Test FloatToDecimalValidator with valid floats. """
        validator = FloatToDecimalValidator()
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert str(decimal) == expected_decimal_str

    @staticmethod
    def test_invalid_none():
        """ Check that FloatToDecimalValidator raises exception for None as value. """
        validator = FloatToDecimalValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', [123, 'banana', '1.234', True, [1.234]])
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
        'min_value, max_value, input_data, expected_decimal_str', [
            # min_value only (as float)
            *unpack_params(
                3.0, None,
                [
                    (3.0, '3.0'),
                    (3.001, '3.001'),
                    (9.999, '9.999'),
                ],
            ),

            # max_value only (as float)
            *unpack_params(
                None, 10.0,
                [
                    (-999.0, '-999.0'),
                    (9.9, '9.9'),
                    (10.0, '10.0'),
                ],
            ),

            # min_value and max_value (as int)
            *unpack_params(
                0, 1,
                [
                    (0.0, '0.0'),
                    (0.001, '0.001'),
                    (0.999, '0.999'),
                    (1.0, '1.0'),
                ],
            ),

            # min_value and max_value (as Decimal and str)
            *unpack_params(
                Decimal('-1.0'), '1.0',
                [
                    (-1.0, '-1.0'),
                    (-0.999, '-0.999'),
                    (0.999, '0.999'),
                    (1.0, '1.0'),
                ],
            ),
        ]
    )
    def test_float_value_range_valid(min_value, max_value, input_data, expected_decimal_str):
        """ Test FloatToDecimalValidator with range requirements with valid floats. """
        validator = FloatToDecimalValidator(min_value=min_value, max_value=max_value)
        output_value = validator.validate(input_data)
        assert type(output_value) is Decimal
        assert str(output_value) == expected_decimal_str

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data', [
            # min_value only (as float)
            *unpack_params(
                3.0, None,
                [2.999, 2.9, -3.0],
            ),

            # max_value only (as float)
            *unpack_params(
                None, 10.0,
                [10.001, 11.0, 999.0],
            ),

            # min_value and max_value (as int)
            *unpack_params(
                0, 1,
                [-1.0, -0.001, 1.001, 1.1],
            ),

            # min_value and max_value (as Decimal and str)
            *unpack_params(
                Decimal('-1.0'), '1.0',
                [-1.1, -1.001, 1.001, 1.1],
            ),
        ]
    )
    def test_float_value_range_invalid(min_value, max_value, input_data):
        """ Test FloatToDecimalValidator with range requirements with invalid floats. """
        validator = FloatToDecimalValidator(min_value=min_value, max_value=max_value)

        # Construct error dict with min_value and/or max_value, depending on which is specified
        expected_error_dict = {'code': 'number_range_error'}
        expected_error_dict.update({'max_value': str(max_value)} if max_value is not None else {})
        expected_error_dict.update({'min_value': str(min_value)} if min_value is not None else {})

        with pytest.raises(NumberRangeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == expected_error_dict

    # Test optional allow_integers parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_str', [
            # Floats should still work of course
            (1.234, '1.234'),
            (-123.4, '-123.4'),
            # Integers shouldn't have trailing '.0' in the decimal output
            (0, '0'),
            (42, '42'),
            (-123, '-123'),
        ]
    )
    def test_allow_integers_valid(input_data, expected_decimal_str):
        """ Test FloatToDecimalValidator with allow_integers=True with valid input (both as floats and integers). """
        validator = FloatToDecimalValidator(allow_integers=True)
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert str(decimal) == expected_decimal_str

    @staticmethod
    def test_allow_integers_with_invalid_type():
        """ Test that FloatToDecimalValidator with allow_integers=True only accepts floats and integers. """
        validator = FloatToDecimalValidator(allow_integers=True)
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate('1.234')
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['float', 'int'],
        }

    @staticmethod
    def test_allow_integers_with_value_range():
        """ Test FloatToDecimalValidator with allow_integers=True and a value range. """
        validator = FloatToDecimalValidator(min_value=-1.9, max_value=10.0, allow_integers=True)

        # Valid input
        assert str(validator.validate(-1)) == '-1'
        assert str(validator.validate(10)) == '10'
        assert str(validator.validate(-1.9)) == '-1.9'
        assert str(validator.validate(10.0)) == '10.0'

        # Invalid input
        for input_value in [-2, 11, -1.91, 10.1]:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_value)
            assert exception_info.value.to_dict() == {
                'code': 'number_range_error',
                'min_value': '-1.9',
                'max_value': '10.0',
            }

    # Test optional allow_strings parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_str', [
            # Floats should still work of course
            (1.234, '1.234'),
            (-123.4, '-123.4'),
            # Decimal strings
            ('0', '0'),
            ('123', '123'),
            ('123.0', '123.0'),
            ('-1.23', '-1.23'),
        ]
    )
    def test_allow_strings_valid(input_data, expected_decimal_str):
        """ Test FloatToDecimalValidator with allow_strings=True with valid input (both as floats and strings). """
        validator = FloatToDecimalValidator(allow_strings=True)
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert str(decimal) == expected_decimal_str

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'banana', '1234x', '$123', '1,234', 'Infinity', 'NaN', '.', '1e3'])
    def test_allow_strings_with_invalid_strings(input_data):
        """ Test that FloatToDecimalValidator with allow_strings=True raises exceptions for invalid or malformed strings. """
        validator = FloatToDecimalValidator(allow_strings=True)
        with pytest.raises(InvalidDecimalError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_decimal',
        }

    @staticmethod
    def test_allow_strings_with_invalid_type():
        """ Test that FloatToDecimalValidator with allow_strings=True only accepts floats and strings. """
        validator = FloatToDecimalValidator(allow_strings=True)
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['float', 'str'],
        }

    @staticmethod
    def test_allow_strings_with_value_range():
        """ Test FloatToDecimalValidator with allow_strings=True and a value range. """
        validator = FloatToDecimalValidator(min_value='-1.9', max_value='10.0', allow_strings=True)

        # Valid input
        assert str(validator.validate('-1.9')) == '-1.9'
        assert str(validator.validate('10.0')) == '10.0'

        # Invalid input
        for input_value in ['-1.91', '10.1']:
            with pytest.raises(NumberRangeError) as exception_info:
                validator.validate(input_value)
            assert exception_info.value.to_dict() == {
                'code': 'number_range_error',
                'min_value': '-1.9',
                'max_value': '10.0',
            }

    # Test combination of allow_integers and allow_strings

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_str', [
            # Floats
            (0.0, '0.0'),
            (1.234, '1.234'),
            (-123.4, '-123.4'),
            # Integers
            (0, '0'),
            (42, '42'),
            (-123, '-123'),
            # Decimal strings
            ('0', '0'),
            ('123', '123'),
            ('-123.0', '-123.0'),
        ]
    )
    def test_allow_integers_and_strings_valid(input_data, expected_decimal_str):
        """ Test FloatToDecimalValidator with allow_integers=True AND allow_strings=True with valid input. """
        validator = FloatToDecimalValidator(allow_integers=True, allow_strings=True)
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert str(decimal) == expected_decimal_str

    @staticmethod
    def test_allow_integers_and_strings_with_invalid_strings():
        """ Test that FloatToDecimalValidator with allow_integers=True AND allow_strings=True raises exceptions for invalid strings. """
        validator = FloatToDecimalValidator(allow_integers=True, allow_strings=True)
        with pytest.raises(InvalidDecimalError) as exception_info:
            validator.validate('banana')
        assert exception_info.value.to_dict() == {
            'code': 'invalid_decimal',
        }

    @staticmethod
    def test_allow_integers_and_strings_with_invalid_type():
        """ Check that FloatToDecimalValidator with allow_integers=True AND allow_strings=True only accepts float, int and str. """
        validator = FloatToDecimalValidator(allow_integers=True, allow_strings=True)
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(True)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['float', 'int', 'str'],
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
            # output_places=3
            (3, 0.0, '0.000'),
            (3, -42.0, '-42.000'),
            (3, 42.0, '42.000'),
            (3, 123.456, '123.456'),
            (3, 123.456789, '123.457'),
        ]
    )
    def test_output_places(output_places, input_data, expected_decimal_str):
        """ Test FloatToDecimalValidator with output_places parameter (fixed number of decimal places in output value). """
        validator = FloatToDecimalValidator(output_places=output_places)
        decimal = validator.validate(input_data)
        assert type(decimal) is Decimal
        assert str(decimal) == expected_decimal_str

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
