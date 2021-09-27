# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest
import re

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, RegexMatchError, StringInvalidLengthError
from wtfjson.validators import RegexValidator


class RegexValidatorTest:
    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that RegexValidator raises exception for None as value. """
        validator = RegexValidator(re.compile(r'.*'))
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that RegexValidator raises exceptions for values that are not of type 'str'. """
        validator = RegexValidator(re.compile(r'.*'))
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    # Test RegexValidator with precompiled regex patterns

    @staticmethod
    @pytest.mark.parametrize(
        'regex_pattern, valid_input_list', [
            (r'', ['']),
            (r'banana', ['banana']),
            (r'^banana$', ['banana']),
            (r'.*', ['', 'banana', '123']),
            (r'[0-9]+', ['0', '3', '12345', '00000']),
            (r'[0-9]+.*', ['0', '3', '12345', '13 bananas']),
            (r'\w+\.(png|jpg)', ['banana123.png', 'green_apple.jpg']),
        ]
    )
    def test_precompiled_pattern_valid(regex_pattern, valid_input_list):
        """ Test RegexValidator with precompiled patterns and valid input. """
        precompiled_pattern = re.compile(regex_pattern)
        validator = RegexValidator(precompiled_pattern)

        for valid_input in valid_input_list:
            assert validator.validate(valid_input) == valid_input

    @staticmethod
    @pytest.mark.parametrize(
        'regex_pattern, invalid_input_list', [
            (r'', ['a', ' ', '\n', '^$']),
            (r'banana', ['', 'bananana', 'BANANA', 'banana\nbanana']),
            (r'^banana$', ['', 'bananana', 'BANANA', 'banana\nbanana']),
            (r'.+', ['', '\n', 'a\nb']),
            (r'[0-9]+', ['', 'a', '13 bananas', 'banana 13', '13\n12']),
            (r'[0-9]+.*', ['', 'a', 'banana 13']),
            (r'\w+\.(png|jpg)', ['', '.png', 'bananajpg', 'banana.pngx', 'ba\nana.png']),
        ]
    )
    def test_precompiled_pattern_invalid(regex_pattern, invalid_input_list):
        """ Test RegexValidator with precompiled patterns and invalid input. """
        precompiled_pattern = re.compile(regex_pattern)
        validator = RegexValidator(precompiled_pattern, multiline=True)

        for invalid_input in invalid_input_list:
            with pytest.raises(RegexMatchError) as exception_info:
                validator.validate(invalid_input)
            assert exception_info.value.to_dict() == {'code': 'invalid_string_format'}

    # Test RegexValidator with regex flags (ignorecase, multiline, ...)

    @staticmethod
    @pytest.mark.parametrize(
        'regex_pattern, regex_flags, valid_input_list', [
            # Case-insensitive matching (i)
            (r'banana', re.IGNORECASE, ['banana', 'BANANA', 'BaNaNa']),
            (r'[0-9a-z]+', re.IGNORECASE, ['0123', 'abcd42', 'ABCD42']),
            # Multiline (m)
            (r'(^banana$\n*)+', re.MULTILINE, ['banana', 'banana\nbanana', 'banana\n\nbanana\n']),
            (r'(^[0-9]+\s[a-z]+$\n?)+', re.MULTILINE, ['13 bananas', '13 bananas\n12 apples\n11 strawberries']),
            # Dotall: '.' matches newlines (s)
            (r'foo.bar', re.DOTALL, ['foo-bar', 'foo bar', 'foo\nbar']),
            (r'foo.*bar', re.DOTALL, ['foobar', 'foooooobar', 'foo\nooo\nbar']),

        ]
    )
    def test_pattern_with_flags_valid(regex_pattern, regex_flags, valid_input_list):
        """ Test RegexValidator with precompiled patterns and flags, with valid input. """
        precompiled_pattern = re.compile(regex_pattern, regex_flags)
        validator = RegexValidator(precompiled_pattern, multiline=True)

        for valid_input in valid_input_list:
            assert validator.validate(valid_input) == valid_input

    @staticmethod
    @pytest.mark.parametrize(
        'regex_pattern, regex_flags, invalid_input_list', [
            # Case-insensitive matching (i)
            (r'banana', re.IGNORECASE, ['', 'banano', 'BANANANA']),
            (r'[0-9a-z]+', re.IGNORECASE, ['', '...', '123$banana']),
            # Multiline (m)
            (r'(^banana$\n*)+', re.MULTILINE, ['', 'banano', 'banana\nbanano', 'bananabanana']),
            (r'(^[0-9]+\s[a-z]+$\n?)+', re.MULTILINE, ['', 'banana', '13 bananas 12 apples', 'bananas 13\n12 apples']),
            # Dotall: '.' matches newlines (s)
            (r'foo.bar', re.DOTALL, ['foobar', 'foo  bar', 'foo\n\nbar']),
            (r'foo.*bar', re.DOTALL, ['foo', '\nfoobar\n']),
        ]
    )
    def test_pattern_with_flags_invalid(regex_pattern, regex_flags, invalid_input_list):
        """ Test RegexValidator with precompiled patterns and flags, with invalid input. """
        precompiled_pattern = re.compile(regex_pattern, regex_flags)
        validator = RegexValidator(precompiled_pattern, multiline=True)

        for invalid_input in invalid_input_list:
            with pytest.raises(RegexMatchError) as exception_info:
                validator.validate(invalid_input)
            assert exception_info.value.to_dict() == {'code': 'invalid_string_format'}

    # Test RegexValidator with (non-precompiled) string patterns

    @staticmethod
    @pytest.mark.parametrize('pattern_str', [r'', r'banana', r'[0-9]+.*', r'\w+\.(png|jpg)'])
    def test_string_pattern_compiled_correctly(pattern_str):
        """ Check that RegexValidator handles non-precompiled patterns (as strings) correctly. """
        validator = RegexValidator(pattern_str)
        assert validator.regex_pattern == re.compile(pattern_str)

    # Test RegexValidator with invalid regex pattern

    @staticmethod
    def test_invalid_regex_pattern():
        """ Check that RegexValidator raises an exception for invalid regex patterns. """
        with pytest.raises(re.error) as exception_info:
            RegexValidator('[')
        assert str(exception_info.value) == 'unterminated character set at position 0'

    # Test RegexValidator with custom error code

    @staticmethod
    def test_custom_error_code():
        """ Test RegexValidator with a custom error code. """
        validator = RegexValidator('[0-9]{5}', custom_error_code='invalid_zip_code')

        # Valid input
        assert validator.validate('12345') == '12345'

        # Invalid input
        with pytest.raises(RegexMatchError) as exception_info:
            validator.validate('abcde')
        assert exception_info.value.to_dict() == {'code': 'invalid_zip_code'}

    # Tests with length requirements

    @staticmethod
    @pytest.mark.parametrize('input_data', ['0000', '0001', '1337', '00000', '99999'])
    def test_string_length_requirements_valid(input_data):
        """ Test RegexValidator with StringValidator length requirements, with valid input. """
        validator = RegexValidator('[0-9]*', min_length=4, max_length=5)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', '0', '000', 'abc', '000000', '123456', 'abcdef'])
    def test_string_min_max_length_invalid(input_data):
        """ Test RegexValidator with StringValidator length requirements, with invalid input. """
        validator = RegexValidator('[0-9]*', min_length=4, max_length=5)
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short' if len(input_data) < 4 else 'string_too_long',
            'min_length': 4,
            'max_length': 5,
        }
