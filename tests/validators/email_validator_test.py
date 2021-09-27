# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, StringInvalidLengthError, InvalidEmailError
from wtfjson.validators import EmailValidator


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
        """ Check that EmailValidator raises exceptions for empty strings. """
        validator = EmailValidator()
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate('')
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short',
            'min_length': 1,
            'max_length': 256,
        }

    @staticmethod
    def test_invalid_string_too_long():
        """ Check that EmailValidator raises exceptions for strings that are too long. """
        # Construct an email address that is technically valid but too long
        input_string = ('a' * 64) + '@' + ('very-very-very-very-very-very-very-long-domain.' * 4)
        input_string += 'b' * (257 - len(input_string))

        validator = EmailValidator()
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'min_length': 1,
            'max_length': 256,
        }

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
            'fooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo@example.com'
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
            'foo@bar@example.com'
            # Query part
            'foobar@example.com?subject=foo'
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
