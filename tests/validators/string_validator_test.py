# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, StringTooShortError, StringTooLongError, StringInvalidLengthError, \
    StringInvalidCharactersError, InvalidValidatorOptionException
from wtfjson.validators import StringValidator


class StringValidatorTest:
    # General tests

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

    @staticmethod
    @pytest.mark.parametrize(
        'input_data', [
            '',
            'unit test banana',
            '1234567890',
            '!@#$%^&*()_+-={}[]<>|\\',
        ]
    )
    def test_valid_string(input_data):
        """ Test StringValidator with valid strings. """
        validator = StringValidator()
        assert validator.validate(input_data) == input_data

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
    @pytest.mark.parametrize(
        'input_data, error_code', [
            ('', 'string_too_short'),
            ('banan', 'string_too_short'),
            ('bananana', 'string_too_long'),
        ]
    )
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

    # Tests for unsafe and multiline strings

    @staticmethod
    @pytest.mark.parametrize(
        'multiline, unsafe, input_string, expected_result', [
            # Safe multiline strings
            (True, False, 'singleline', 'singleline'),
            (True, False, 'foo\nbar', 'foo\nbar'),
            (True, False, 'foo\rbar\r\nbaz\n', 'foo\nbar\nbaz\n'),

            # Unsafe multiline strings (no normalization of line separators)
            (True, True, 'foo\nbar\0baz', 'foo\nbar\0baz'),
            (True, True, 'foo\rbar\r\nbaz\n', 'foo\rbar\r\nbaz\n'),

            # Unsafe singleline strings
            (False, True, '\0', '\0'),
            (False, True, 'foo\tbar\x1fbaz\0', 'foo\tbar\x1fbaz\0'),
        ]
    )
    def test_unsafe_and_multiline_strings_valid(multiline, unsafe, input_string, expected_result):
        """ Test StringValidator with different multiline and unsafe settings with valid strings. """
        validator = StringValidator(multiline=multiline, unsafe=unsafe)
        assert validator.validate(input_string) == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        'multiline, unsafe, input_string, error_reason', [
            # Default: Safe singleline strings (no non-printable characters including newlines)
            (False, False, 'foo\nbar', 'No multiline strings allowed.'),
            (False, False, 'foo\rbar', 'No multiline strings allowed.'),
            (False, False, 'foo\0bar', 'String contains non-printable characters.'),
            (False, False, '\x1f', 'String contains non-printable characters.'),

            # Safe multiline strings (no non-printable characters except newlines)
            (True, False, '\0', 'String contains non-printable characters.'),
            (True, False, 'foo\nbar\tbaz', 'String contains non-printable characters.'),
            (True, False, '\x1f', 'String contains non-printable characters.'),

            # Unsafe singleline strings (non-printable characters allowed, except for newlines)
            (False, True, 'foo\nbar', 'No multiline strings allowed.'),
            (False, True, 'foo\rbar', 'No multiline strings allowed.'),
        ]
    )
    def test_unsafe_and_multiline_strings_invalid(multiline, unsafe, input_string, error_reason):
        """ Test StringValidator with different multiline and unsafe settings with invalid strings. """
        validator = StringValidator(multiline=multiline, unsafe=unsafe)
        with pytest.raises(StringInvalidCharactersError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'string_invalid_characters',
            'reason': error_reason,
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
