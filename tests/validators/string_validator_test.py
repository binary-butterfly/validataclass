# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, StringTooShortError, StringTooLongError, StringInvalidLengthError, \
    InvalidValidatorOptionException
from wtfjson.validators import StringValidator


class StringValidatorTest:
    @staticmethod
    def test_valid_string():
        """ Test StringValidator with valid strings. """
        validator = StringValidator()
        assert validator.validate('') == ''
        assert validator.validate('unit test banana') == 'unit test banana'

    @staticmethod
    def test_invalid_none():
        """ Check that StringValidator raises exceptions for None as value. """
        validator = StringValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that StringValidator raises exceptions for values that are not of type 'str'. """
        validator = StringValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    # Test length requirement checks: Only min_length specified

    @staticmethod
    @pytest.mark.parametrize('input_data', ['abc', 'banana', '1234567890abcdef'])
    def test_string_min_length_valid(input_data):
        """ Test StringValidator with minimum length requirement with a list of valid strings. """
        validator = StringValidator(min_length=3)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'a', 'ab'])
    def test_string_min_length_too_short(input_data):
        """ Test StringValidator with minimum length requirement with a list of strings that are too short. """
        validator = StringValidator(min_length=3)
        with pytest.raises(StringTooShortError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short',
            'min_length': 3,
        }

    # Test length requirement checks: Only max_length specified

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'a', 'banana', '1234567890'])
    def test_string_max_length_valid(input_data):
        """ Test StringValidator with maximum length requirement with a list of valid strings. """
        validator = StringValidator(max_length=10)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data', ['1234567890a', '1234567890abcdef'])
    def test_string_max_length_too_long(input_data):
        """ Test StringValidator with maximum length requirement with a list of strings that are too long. """
        validator = StringValidator(max_length=10)
        with pytest.raises(StringTooLongError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'max_length': 10,
        }

    # Test length requirement checks: Both min_length and max_length specified

    @staticmethod
    @pytest.mark.parametrize('input_data', ['abc', 'banana', '1234567890'])
    def test_string_min_max_length_valid(input_data):
        """ Test StringValidator with both minimum and maximum length requirement with a list of valid strings. """
        validator = StringValidator(min_length=3, max_length=10)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, error_code', [
            ('', 'string_too_short'),
            ('a', 'string_too_short'),
            ('ab', 'string_too_short'),
            ('1234567890a', 'string_too_long'),
            ('1234567890abcdef', 'string_too_long'),
        ]
    )
    def test_string_min_max_length_invalid(input_data, error_code):
        """ Test StringValidator with both minimum and maximum length requirement with strings that are too short or too long. """
        validator = StringValidator(min_length=3, max_length=10)
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': error_code,
            'min_length': 3,
            'max_length': 10,
        }

    # Test length requirement checks: min_length equals max_length

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', '000000'])
    def test_string_exact_length_valid(input_data):
        """ Test StringValidator with exact length requirement (minimum = maximum) with valid strings. """
        validator = StringValidator(min_length=6, max_length=6)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data, error_code', [
        ('', 'string_too_short'),
        ('banan', 'string_too_short'),
        ('bananana', 'string_too_long'),
    ])
    def test_string_exact_length_invalid(input_data, error_code):
        """ Test StringValidator with exact length requirement (minimum = maximum) with strings that are too short or too long. """
        validator = StringValidator(min_length=6, max_length=6)
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': error_code,
            'min_length': 6,
            'max_length': 6,
        }

    # Invalid validator parameters

    @staticmethod
    def test_min_length_greater_than_max_length():
        """ Check that StringValidator raises exception when min_length is greater than max_length. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            StringValidator(min_length=4, max_length=3)
        assert str(exception_info.value) == 'Parameter "min_length" cannot be greater than "max_length".'

    @staticmethod
    def test_min_length_negative():
        """ Check that StringValidator raises exception when min_length is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            StringValidator(min_length=-1)
        assert str(exception_info.value) == 'Parameter "min_length" cannot be negative.'

    @staticmethod
    def test_max_length_negative():
        """ Check that StringValidator raises exception when max_length is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            StringValidator(max_length=-1)
        assert str(exception_info.value) == 'Parameter "max_length" cannot be negative.'
