"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import RequiredValueError, InvalidTypeError, StringInvalidLengthError, InvalidEmailError
from validataclass.validators import EmailValidator


class EmailValidatorTest:
    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that EmailValidator raises exceptions for None as value. """
        validator = EmailValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that EmailValidator raises exceptions for values that are not of type 'str'. """
        validator = EmailValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    @staticmethod
    def test_invalid_empty_string():
        """ Check that EmailValidator raises exceptions for empty strings by default. """
        validator = EmailValidator()
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate('')
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short',
            'min_length': 1,
            'max_length': 256,
        }

    # Test optional allow_empty parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Empty strings
            '',
            # Regular addresses
            'a@example.com',
        ]
    )
    def test_allow_empty_valid(input_string):
        """ Test that EmailValidator returns empty string if boolean parameter allow_empty=True. """
        validator = EmailValidator(allow_empty=True)
        assert validator.validate(input_string) == input_string

    # Test maximum string length

    @staticmethod
    @pytest.mark.parametrize('allow_empty', [True, False])
    def test_invalid_string_too_long(allow_empty):
        """ Test that EmailValidator raises exceptions for strings that are too long. """
        # Construct an email address that is technically valid but too long
        input_string = ('a' * 64) + '@' + ('very-very-very-very-very-very-very-long-domain.' * 4)
        input_string += 'b' * (257 - len(input_string))

        validator = EmailValidator(allow_empty=allow_empty)
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'min_length': 0 if allow_empty else 1,
            'max_length': 256,
        }

    @staticmethod
    def test_max_length_parameter():
        """ Test EmailValidator with a custom value for max_length. """
        validator = EmailValidator(max_length=16)

        # Valid input (16 characters)
        assert validator.validate('abcd@example.com')

        # Invalid input (17 characters)
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate('abcde@example.com')
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'min_length': 1,
            'max_length': 16,
        }

    # Test to_lowercase option

    @staticmethod
    @pytest.mark.parametrize(
        'to_lowercase, input_string, expected_output', [
            # Default behaviour: Keep uppercase letters intact
            (False, 'foo@example.com', 'foo@example.com'),
            (False, 'Foo.Bar@Example.COM', 'Foo.Bar@Example.COM'),

            # Set to_lowercase=True
            (True, 'foo@example.com', 'foo@example.com'),
            (True, 'Foo.Bar@Example.COM', 'foo.bar@example.com'),
        ]
    )
    def test_email_to_lowercase(to_lowercase, input_string, expected_output):
        """ Test EmailValidator with the to_lowercase option. """
        validator = EmailValidator(to_lowercase=to_lowercase)
        assert validator.validate(input_string) == expected_output

    # Tests for regex validation of email address format

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Regular addresses (with some odd but valid characters)
            'a@example.com',
            '~foo-123+bar{banana}@some.sub.domain.example.com',
            # Addresses with dots at valid positions
            'foo.bar@example.com',
            'a.b.c.d.e@example.com',
            # Very long local part (up to 64 characters are allowed)
            'fooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo@example.com',
            # Addresses with uppercase letters (should be left intact by default)
            'Foo.Bar@Example.COM',
        ]
    )
    def test_email_regex_valid(input_string):
        """ Test EmailValidator regex validation with valid strings. """
        validator = EmailValidator()
        assert validator.validate(input_string) == input_string

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Invalid characters in local part
            'foo,bar@example.com',
            'foo"bar@example.com',
            'foo\\bar@example.com',
            'foo bar@example.com',
            # Invalid dot positions
            '.banana@example.com',
            'banana.@example.com',
            'bana..na@example.com',
            # Multiple @ characters
            'foo@bar@example.com',
            # Query part
            'foobar@example.com?subject=foo',
        ]
    )
    def test_email_regex_invalid(input_string):
        """ Test EmailValidator regex validation with invalid strings. """
        validator = EmailValidator()
        with pytest.raises(InvalidEmailError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_email',
            'reason': 'Invalid email address format.',
        }

    # Tests for other validation checks

    @staticmethod
    def test_email_local_part_too_long():
        """ Test EmailValidator with a local part that is too long (over 64 characters). """
        validator = EmailValidator()
        with pytest.raises(InvalidEmailError) as exception_info:
            validator.validate('foooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo@example.com')
        assert exception_info.value.to_dict() == {
            'code': 'invalid_email',
            'reason': 'Local part is too long.',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Nonsense domains
            'foobar@$',
            'foobar@$.com',
            # Domains without TLD
            'foobar@localhost',
            'foobar@examplehost',
            # IP addresses
            'foobar@123.45.67.89',
            'foobar@[2001:abc::1234]',
            # Domain label too long
            'foobar@' + ('a' * 70) + '.com',
        ]
    )
    def test_email_domain_invalid(input_string):
        """ Test EmailValidator with invalid domains. """
        validator = EmailValidator()
        with pytest.raises(InvalidEmailError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_email',
            'reason': 'Domain not valid.',
        }
