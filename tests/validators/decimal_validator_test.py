"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import decimal
from decimal import Decimal

import pytest

from tests.test_utils import assert_decimal, unpack_params
from validataclass.exceptions import RequiredValueError, InvalidTypeError, InvalidDecimalError, NumberRangeError, \
    DecimalPlacesError, InvalidValidatorOptionException
from validataclass.validators import DecimalValidator


class DecimalValidatorTest:
    """
    Unit tests for DecimalValidator.
    """

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_decimal_str',
        [
            ('0', '0'),
            ('1.234', '1.234'),
            ('-0.001', '-0.001'),
            ('+42', '42'),
            ('-.1', '-0.1'),
            ('-1.', '-1'),
            ('-123456789.123456789', '-123456789.123456789'),
        ]
    )
    def test_valid_decimal(input_data, expected_decimal_str):
        """ Test DecimalValidator with valid input strings. """
        validator = DecimalValidator()
        assert_decimal(validator.validate(input_data), expected_decimal_str)

    @staticmethod
    def test_invalid_none():
        """ Check that DecimalValidator raises exceptions for None as value. """
        validator = DecimalValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', [1234, 1.234, True])
    def test_invalid_wrong_type(input_data):
        """ Check that DecimalValidator raises exceptions for values that are not of type 'str'. """
        validator = DecimalValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'bananana', '1234x', '$123', '1,234', 'Infinity', 'NaN', '.', '1e3'])
    def test_invalid_malformed_string(input_data):
        """ Test DecimalValidator with malformed strings. """
        validator = DecimalValidator()
        with pytest.raises(InvalidDecimalError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'invalid_decimal'}

    # Test value range requirement check

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data', [
            # min_value only (as Decimal object and as string)
            *unpack_params(
                Decimal('1'), None,
                ['1', '1.000', '1.00001', '+1.1', '42'],
            ),
            *unpack_params(
                '-3.000', None,
                ['-3', '-2.9999', '-2', '0.000', '1.234', '4.567'],
            ),

            # max_value only
            *unpack_params(
                None, Decimal('-10.5'),
                ['-10.5', '-10.6', '-11', '-9999.999'],
            ),
            *unpack_params(
                None, '-0',
                ['-1.234', '-0.001', '0', '-0', '+0'],
            ),

            # min_value and max_value (as Decimal, integer and string)
            *unpack_params(
                Decimal('0'), Decimal('10'),
                ['0.000', '0.001', '1', '9.9999', '+10.00000'],
            ),
            *unpack_params(
                -1, 1,
                ['-1.0000', '-0.99999', '-0.0001', '0', '0.001', '0.9999', '1.000'],
            ),
            *unpack_params(
                Decimal('42'), '42.0',
                ['42', '+42', '42.0000000'],
            ),
        ]
    )
    def test_decimal_value_range_valid(min_value, max_value, input_data):
        """ Test DecimalValidator with range requirements with valid decimal strings. """
        validator = DecimalValidator(min_value=min_value, max_value=max_value)
        assert_decimal(validator.validate(input_data), input_data.lstrip('+').rstrip('.'))

    @staticmethod
    @pytest.mark.parametrize(
        'min_value, max_value, input_data', [
            # min_value only (as Decimal object and as string)
            *unpack_params(
                Decimal('1'), None,
                ['0.9999', '0', '-1.00001', '-42'],
            ),
            *unpack_params(
                '-3.000', None,
                ['-3.000000001', '-3.1', '-42'],
            ),

            # max_value only
            *unpack_params(
                None, Decimal('-10.5'),
                ['-10.499', '-10.000', '-10', '0', '0.001', '42'],
            ),
            *unpack_params(
                None, '-0',
                ['0.001', '1', '123.456'],
            ),

            # min_value and max_value
            *unpack_params(
                Decimal('0'), Decimal('10'),
                ['-0.001', '-1', '10.0000001', '+42'],
            ),
            *unpack_params(
                '-1', '1',
                ['-1.0001', '-9.999', '1.000001', '1.234', '+42'],
            ),
            *unpack_params(
                Decimal('42'), '42.0',
                ['0', '41.999999', '42.00000001', '-42'],
            ),
        ]
    )
    def test_decimal_value_range_invalid(min_value, max_value, input_data):
        """ Test DecimalValidator with range requirements with decimal strings outside the range. """
        validator = DecimalValidator(min_value=min_value, max_value=max_value)

        # Construct error dict with min_value and/or max_value, depending on which is specified
        expected_error_dict = {'code': 'number_range_error'}
        expected_error_dict.update({'min_value': str(min_value)} if min_value is not None else {})
        expected_error_dict.update({'max_value': str(max_value)} if max_value is not None else {})

        with pytest.raises(NumberRangeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == expected_error_dict

    # Test minimum/maximum decimal places requirements

    @staticmethod
    @pytest.mark.parametrize(
        'min_places, max_places, input_data', [
            # min_places only
            *unpack_params(
                0, None,
                ['0', '0.001', '0.10', '-123.456789', '42'],
            ),
            *unpack_params(
                1, None,
                ['0.0', '0.001', '0.10', '-123.456789', '42.0'],
            ),
            *unpack_params(
                3, None,
                ['0.000', '0.001', '0.100', '-123.456789', '42.000'],
            ),

            # max_places only
            *unpack_params(
                None, 0,
                ['0', '-123', '42.'],
            ),
            *unpack_params(
                None, 1,
                ['0', '0.0', '0.1', '-123.4', '42'],
            ),
            *unpack_params(
                None, 3,
                ['0', '0.10', '0.01', '123.4', '-123.456', '42.'],
            ),

            # min_places and max_places
            *unpack_params(
                0, 2,
                ['0', '0.0', '0.01', '0.1', '-123', '-123.45', '42.'],
            ),
            *unpack_params(
                2, 3,
                ['0.00', '0.000', '0.10', '0.001', '-123.45', '-123.456'],
            ),
            *unpack_params(
                2, 2,
                ['0.00', '0.01', '0.10', '-123.45', '42.00'],
            ),
        ]
    )
    def test_min_max_places_valid(min_places, max_places, input_data):
        """ Test DecimalValidator with a minimum and/or maximum number of decimal places with valid decimal strings. """
        validator = DecimalValidator(min_places=min_places, max_places=max_places)
        assert_decimal(validator.validate(input_data), input_data.rstrip('.'))

    @staticmethod
    @pytest.mark.parametrize(
        'min_places, max_places, input_data', [
            # min_places only
            *unpack_params(
                1, None,
                ['0', '0.', '-123', '42.'],
            ),
            *unpack_params(
                3, None,
                ['0', '0.01', '-123.45'],
            ),

            # max_places only
            *unpack_params(
                None, 0,
                ['0.0', '-123.4', '42.0', '0.1'],
            ),
            *unpack_params(
                None, 1,
                ['0.00', '0.01', '-123.45'],
            ),
            *unpack_params(
                None, 3,
                ['0.0000', '0.1000', '-123.4567'],
            ),

            # min_places and max_places
            *unpack_params(
                2, 3,
                ['0.0', '0.0000', '0.1', '0.0001', '-123.4', '-123.4567', '42'],
            ),
            *unpack_params(
                2, 2,
                ['0.0', '0.000', '0.001', '0.1', '-123.4', '-123.456', '42'],
            ),
        ]
    )
    def test_min_max_places_invalid(min_places, max_places, input_data):
        """ Test DecimalValidator with a minimum and/or maximum number of decimal places with invalid input. """
        validator = DecimalValidator(min_places=min_places, max_places=max_places)

        # Construct error dict with min_places and/or max_places, depending on which is specified
        expected_error_dict = {'code': 'decimal_places'}
        expected_error_dict.update({'min_places': min_places} if min_places is not None else {})
        expected_error_dict.update({'max_places': max_places} if max_places is not None else {})

        with pytest.raises(DecimalPlacesError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == expected_error_dict

    # Test output_places and rounding parameters

    @staticmethod
    @pytest.mark.parametrize(
        'output_places, input_data, expected_output',
        [
            # output_places=0
            (0, '0', '0'),
            (0, '-42', '-42'),
            (0, '42.0', '42'),
            (0, '123.456', '123'),  # rounded down
            (0, '123.567', '124'),  # rounded up

            # output_places=1
            (1, '0', '0.0'),
            (1, '-42', '-42.0'),
            (1, '42.000', '42.0'),
            (1, '123.456', '123.5'),
            (1, '999.999', '1000.0'),

            # output_places=3
            (3, '0', '0.000'),
            (3, '-42', '-42.000'),
            (3, '42.000000', '42.000'),
            (3, '123.456', '123.456'),
            (3, '123.456789', '123.457'),

            # output_places=9
            (9, '1.234', '1.234000000')
        ]
    )
    def test_output_places_default_rounding(output_places, input_data, expected_output):
        """ Test DecimalValidator with a fixed number of output places and the default rounding mode (ROUND_HALF_UP). """
        validator = DecimalValidator(output_places=output_places)
        assert_decimal(validator.validate(input_data), expected_output)

    @staticmethod
    @pytest.mark.parametrize(
        'rounding, input_data, expected_output',
        [
            # Round towards zero
            (decimal.ROUND_DOWN, '1.00', '1.0'),
            (decimal.ROUND_DOWN, '1.05', '1.0'),
            (decimal.ROUND_DOWN, '1.09', '1.0'),
            (decimal.ROUND_DOWN, '-1.09', '-1.0'),

            # Round away from zero
            (decimal.ROUND_UP, '1.00', '1.0'),
            (decimal.ROUND_UP, '1.01', '1.1'),
            (decimal.ROUND_UP, '1.09', '1.1'),
            (decimal.ROUND_UP, '-1.01', '-1.1'),

            # Round towards -Infinity
            (decimal.ROUND_FLOOR, '1.00', '1.0'),
            (decimal.ROUND_FLOOR, '1.09', '1.0'),
            (decimal.ROUND_FLOOR, '-1.01', '-1.1'),

            # Round to nearest with ties going to nearest even integer (used by decimal.DefaultContext)
            (decimal.ROUND_HALF_EVEN, '1.04', '1.0'),
            (decimal.ROUND_HALF_EVEN, '1.05', '1.0'),
            (decimal.ROUND_HALF_EVEN, '1.14', '1.1'),
            (decimal.ROUND_HALF_EVEN, '1.15', '1.2'),
        ]
    )
    def test_with_different_rounding_modes(rounding, input_data, expected_output):
        """ Test DecimalValidator with a fixed number of output places and different rounding modes. """
        validator = DecimalValidator(output_places=1, rounding=rounding)
        assert_decimal(validator.validate(input_data), expected_output)

    @staticmethod
    def test_with_rounding_mode_from_decimal_context():
        """ Test DecimalValidator with rounding=None to use the rounding mode of the decimal context. """
        validator = DecimalValidator(output_places=1, rounding=None)
        with decimal.localcontext() as ctx:
            ctx.rounding = decimal.ROUND_CEILING
            assert_decimal(validator.validate('1.01'), '1.1')
            assert_decimal(validator.validate('-1.09'), '-1.0')

    # Invalid validator parameters

    @staticmethod
    def test_min_value_greater_than_max_value():
        """ Check that DecimalValidator raises exception when min_value is greater than max_value. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DecimalValidator(min_value='4.0', max_value='3.9')
        assert str(exception_info.value) == 'Parameter "min_value" cannot be greater than "max_value".'

    @staticmethod
    def test_min_places_negative():
        """ Check that DecimalValidator raises exception when min_places is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DecimalValidator(min_places=-1)
        assert str(exception_info.value) == 'Parameter "min_places" cannot be negative.'

    @staticmethod
    def test_max_places_negative():
        """ Check that DecimalValidator raises exception when max_places is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DecimalValidator(max_places=-1)
        assert str(exception_info.value) == 'Parameter "max_places" cannot be negative.'

    @staticmethod
    def test_min_places_greater_than_max_places():
        """ Check that DecimalValidator raises exception when min_places is greater than max_places. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DecimalValidator(min_places=3, max_places=2)
        assert str(exception_info.value) == 'Parameter "min_places" cannot be greater than "max_places".'

    @staticmethod
    def test_output_places_negative():
        """ Check that DecimalValidator raises exception when output_places is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DecimalValidator(output_places=-1)
        assert str(exception_info.value) == 'Parameter "output_places" cannot be negative.'
