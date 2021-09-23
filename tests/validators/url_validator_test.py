# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, StringInvalidLengthError, InvalidUrlError
from wtfjson.validators import UrlValidator


class UrlValidatorTest:
    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that UrlValidator raises exceptions for None as value. """
        validator = UrlValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that UrlValidator raises exceptions for values that are not of type 'str'. """
        validator = UrlValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    @staticmethod
    def test_invalid_empty_string():
        """ Check that UrlValidator raises exceptions for empty strings. """
        validator = UrlValidator()
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate('')
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short',
            'min_length': 1,
            'max_length': 2000,
        }

    @staticmethod
    def test_invalid_string_too_long():
        """ Check that UrlValidator raises exceptions for strings that are too long. """
        # Construct a URL that is technically valid but too long
        input_string = 'https://example.com/'
        input_string += 'a' * (2001 - len(input_string))

        validator = UrlValidator()
        with pytest.raises(StringInvalidLengthError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'min_length': 1,
            'max_length': 2000,
        }

    # Tests for regex validation of URL format

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            'https://example.com',
            'https://example.com/foo/bar.html#baz',
            'https://example.com/foo%20bar.html%3Ffoo%3Dbar',
            'https://foo.bar.baz.example.com/foo.html',
            'http://localhost/',
            'http://123.45.67.89:8080/?foo=bar',
            'http://user:password@[2001:abc::1234]:8080?foo=bar#baz@bloop',
            'ftp://user@examplehost/file/path',
            'git://github.com/binary-butterfly/wtfjson.git',
            'git+https://github.com/binary-butterfly/wtfjson@0.3.0#egg=wtfjson',
        ]
    )
    def test_url_regex_valid(input_string):
        """ Test UrlValidator regex validation with valid strings. """
        # Choose options to be most permissive to focus on the regex validation (allow any scheme, etc.)
        validator = UrlValidator(allowed_schemes=[], require_tld=False, allow_ip=True, allow_userinfo=True)
        assert validator.validate(input_string) == input_string

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # No or invalid scheme, missing delimiters
            '://example.com',
            '123://example.com',
            'http//example.com',
            'http:example.com',
            # Empty or invalid host
            'https://',
            'https:///path',
            'https://example.com@',
            'https://@example.com',
            'https://[2001:abc::1234/foo/bar',
            # Invalid port
            'https://example.com:/foo/bar',
            'https://example.com:0/foo/bar',
            # Invalid URL encoding
            'https://example.com/foo%xxbar',
            'https://example.com/foo%1',
        ]
    )
    def test_url_regex_invalid(input_string):
        """ Test UrlValidator with default options with invalid URL strings that fail the regex validation. """
        validator = UrlValidator(allowed_schemes=[], require_tld=False, allow_ip=True, allow_userinfo=True)
        with pytest.raises(InvalidUrlError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_url',
            'reason': 'Invalid URL format.',
        }

    # Tests with default options

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            'https://example.com',
            'https://sub.domain.example.com/foo/bar',
            'https://xn--hxajbheg2az3al.xn--qxam/?foo=bar',
            'http://123.45.67.89:8080?',
            'http://[2001:abc::1234]:8080?',
        ]
    )
    def test_url_with_default_options_valid(input_string):
        """ Test UrlValidator with default options with valid URL strings. """
        validator = UrlValidator()
        assert validator.validate(input_string) == input_string

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, error_reason', [
            # Invalid scheme
            ('ftp://example.com', 'URL scheme is not allowed.'),
            # No TLD
            ('https://example', 'Invalid host in URL.'),
            ('https://example/foo/bar.com', 'Invalid host in URL.'),
            ('https://example?foo=bar.com', 'Invalid host in URL.'),
            # Invalid domain names and IP addresses
            ('https://$$$.com', 'Invalid host in URL.'),
            ('https://-example.com', 'Invalid host in URL.'),
            ('https://256.256.256.256/foo.bar', 'Invalid host in URL.'),
            ('https://[2001]/foo.bar', 'Invalid host in URL.'),
            ('https://[2001:abc::xxxx]/foo.bar', 'Invalid URL format.'),
            # Contains userinfo
            ('https://username@example.com', 'Userinfo component not allowed in URL.'),
            # Invalid port number
            ('https://example.com:123456/', 'Invalid port number in URL.'),
        ]
    )
    def test_url_with_default_options_invalid(input_string, error_reason):
        """ Test UrlValidator with default options with invalid URL strings. """
        validator = UrlValidator()
        with pytest.raises(InvalidUrlError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_url',
            'reason': error_reason,
        }

    # Tests for allowed_schemes option

    @staticmethod
    @pytest.mark.parametrize(
        'allowed_schemes, input_string', [
            # Default (http and https only)
            (None, 'http://example.com'),
            (None, 'https://example.com'),
            # Empty list means "allow any (valid) scheme"
            ([], 'https://example.com'),
            ([], 'git+https://github.com/foo'),
            ([], 'file://example.com/etc/passwd'),
            # Custom list
            (['ftp', 'gopher'], 'ftp://example.com'),
            (['ftp', 'gopher'], 'gopher://example.com:123/1foobar'),
        ]
    )
    def test_url_allowed_schemes_valid(allowed_schemes, input_string):
        """ Test UrlValidator with `allowed_schemes` option with valid URL strings. """
        validator = UrlValidator(allowed_schemes=allowed_schemes)
        assert validator.validate(input_string) == input_string

    @staticmethod
    @pytest.mark.parametrize(
        'allowed_schemes, input_string', [
            # Default (http and https only)
            (None, 'ftp://example.com'),
            # Custom lists
            (['https'], 'http://example.com'),
            (['ftp', 'gopher'], 'https://example.com'),
        ]
    )
    def test_url_allowed_schemes_invalid(allowed_schemes, input_string):
        """ Test UrlValidator with `allowed_schemes` option with invalid URL strings. """
        validator = UrlValidator(allowed_schemes=allowed_schemes)
        with pytest.raises(InvalidUrlError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_url',
            'reason': 'URL scheme is not allowed.',
        }

    # Tests for boolean validator options

    @staticmethod
    @pytest.mark.parametrize(
        'require_tld, allow_ip, allow_userinfo, input_string', [
            # Domain name with TLD
            (False, False, False, 'https://example.com'),
            (True, True, True, 'https://example.com'),
            # Domain name without TLD
            (False, False, False, 'https://localhost'),
            (False, True, True, 'https://example'),
            # IP addresses
            (False, True, False, 'https://123.45.67.89'),
            (True, True, True, 'https://123.45.67.89'),
            # URLs with userinfo
            (True, False, True, 'https://username@example.com'),
            (False, False, True, 'https://username@localhost'),
            (True, True, True, 'https://username:password@123.45.67.89'),
            # URLs without userinfo
            (False, False, False, 'https://example.com/username@foo.bar'),
        ]
    )
    def test_url_with_boolean_options_valid(require_tld, allow_ip, allow_userinfo, input_string):
        """ Test UrlValidator with various boolean options (require_tld, etc.) with valid URL strings. """
        validator = UrlValidator(require_tld=require_tld, allow_ip=allow_ip, allow_userinfo=allow_userinfo)
        assert validator.validate(input_string) == input_string

    @staticmethod
    @pytest.mark.parametrize(
        'require_tld, allow_ip, allow_userinfo, input_string, error_reason', [
            # Domain name without TLD
            (True, False, False, 'https://localhost#foo.bar', 'Invalid host in URL.'),
            (True, True, True, 'https://example/foo.bar', 'Invalid host in URL.'),
            (True, True, True, 'https://user.name@example', 'Invalid host in URL.'),
            # IP addresses
            (False, False, False, 'https://123.45.67.89', 'Invalid host in URL.'),
            (True, False, True, 'https://[2001:abc::1234]', 'Invalid host in URL.'),
            (True, False, True, 'https://user.name@123.45.67.89', 'Invalid host in URL.'),
            # URLs with userinfo
            (False, True, False, 'https://username@123.45.67.89', 'Userinfo component not allowed in URL.'),
            (True, False, False, 'https://username:123@example.com/foo', 'Userinfo component not allowed in URL.'),
        ]
    )
    def test_url_with_boolean_options_invalid(require_tld, allow_ip, allow_userinfo, input_string, error_reason):
        """ Test UrlValidator with various boolean options (require_tld, etc.) with invalid URL strings. """
        validator = UrlValidator(require_tld=require_tld, allow_ip=allow_ip, allow_userinfo=allow_userinfo)
        with pytest.raises(InvalidUrlError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_url',
            'reason': error_reason,
        }
