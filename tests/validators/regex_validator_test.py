"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import re

import pytest

from tests.test_utils import UNSET_PARAMETER
from validataclass.exceptions import ValidationError, RequiredValueError, InvalidTypeError, RegexMatchError, StringInvalidLengthError
from validataclass.validators import RegexValidator


class UnitTestValidationError(ValidationError):
    """
    Example exception to use as a custom error class in RegexValidator tests.
    """
    code = 'unit_test_error'


class RegexValidatorTest:
    """
    Unit tests for RegexValidator.
    """

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
        with pytest.raises(re.error, match='unterminated character set at position 0'):
            RegexValidator('[')

    # Test RegexValidator with output template

    @staticmethod
    @pytest.mark.parametrize(
        'regex_pattern, output_template, input_data, expected_output', [
            # Empty template returns constant empty output
            (r'.*', r'', 'some input', ''),

            # Constant/no match template
            (r'.*', r'constant template', 'lorem ipsum lololol', 'constant template'),

            # With numeric groups for matches
            (r'(\w+) (\w+)', r'First: \1, Last: \2', "Isaac Newton", "First: Isaac, Last: Newton"),

            # With named groups for matches
            (r'(?P<first>\w+) (?P<last>\w+)', r'First: \g<first>, Last: \g<last>', "Isaac Newton", "First: Isaac, Last: Newton"),
        ]
    )
    def test_templated_output_valid(regex_pattern, output_template, input_data, expected_output):
        """ Check that RegexValidator give templated outputs correctly. """
        validator = RegexValidator(regex_pattern, output_template)
        assert validator.validate(input_data) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        'input_data', [
            'name.jpgg',
            'nonamepng',
            '.png',
            'noext.',
        ]
    )
    def test_templated_output_invalid(input_data):
        """ Check that RegexValidator will raise error instead of returning unfilled templates. """
        pattern = r'(?P<filename>\w+)\.(?P<ext>png|jpg)'
        template = r'Name: \g<filename>; Extension: \g<ext>'
        validator = RegexValidator(pattern, template)

        with pytest.raises(RegexMatchError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {'code': 'invalid_string_format'}

    @staticmethod
    @pytest.mark.parametrize(
        'regex_pattern, output_template, input_data, exception_message', [
            # No numeric match group
            (
                r'.*',
                r'\1',
                'lmao',
                "invalid group reference 1 at position 1",
            ),

            # Nonexisting numeric match group
            (
                r'(\w+) (\w+)',
                r'\3',
                "Isaac Newton",
                "invalid group reference 3 at position 1",
            ),

            # Nonexisting named match group
            (
                r'(?P<first>\w+) (\w+)',
                r'\g<last>',
                "Isaac Newton",
                "unknown group name 'last'",
            ),
        ]
    )
    def test_invalid_output_template(regex_pattern, output_template, input_data, exception_message):
        """ Check that RegexValidator raises exception for invalid templates. """
        validator = RegexValidator(regex_pattern, output_template)
        with pytest.raises((re.error, IndexError)) as exception_info:
            validator.validate(input_data)
        assert str(exception_info.value) == exception_message

    # Test RegexValidator with custom error classes and/or error codes

    @staticmethod
    @pytest.mark.parametrize(
        'custom_error_class, custom_error_code, expected_error_class, expected_error_code',
        [
            # Defaults
            (UNSET_PARAMETER, UNSET_PARAMETER, RegexMatchError, 'invalid_string_format'),

            # Default error class with custom error code
            (UNSET_PARAMETER, 'invalid_zip_code', RegexMatchError, 'invalid_zip_code'),

            # Custom error class with default error code
            (UnitTestValidationError, UNSET_PARAMETER, UnitTestValidationError, 'unit_test_error'),

            # Custom error class with custom error code
            (UnitTestValidationError, 'invalid_zip_code', UnitTestValidationError, 'invalid_zip_code'),
        ]
    )
    def test_custom_errors(custom_error_class, custom_error_code, expected_error_class, expected_error_code):
        """ Test RegexValidator with a custom error classes and/or error codes. """
        # Set validator parameters (use defaults if unset)
        validator_args = {}
        if custom_error_class is not UNSET_PARAMETER:
            validator_args['custom_error_class'] = custom_error_class
        if custom_error_code is not UNSET_PARAMETER:
            validator_args['custom_error_code'] = custom_error_code

        validator = RegexValidator('[0-9]', **validator_args)

        with pytest.raises(ValidationError) as exception_info:
            validator.validate('x')

        assert type(exception_info.value) is expected_error_class
        assert exception_info.value.to_dict() == {'code': expected_error_code}

    @staticmethod
    def test_custom_error_class_invalid_type():
        """ Test that RegexValidator raises an error on construction if the custom error class is not a ValidatonError subclass. """
        with pytest.raises(TypeError, match='Custom error class must be a subclass of ValidationError'):
            RegexValidator('[0-9]', custom_error_class=Exception)  # noqa

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
