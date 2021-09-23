# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.internal import internet_helpers


class InternetHelpersTest:

    # Tests for validate_hostname()

    @staticmethod
    @pytest.mark.parametrize(
        'require_tld, allow_ip, input_string', [
            # Hostnames without TLD
            (False, True, 'example'),
            (False, False, '123-foobar'),

            # Hostnames with TLD
            (False, True, 'example.com'),
            (True, False, '123-foobar.com'),

            # IP addresses
            (True, True, '123.45.67.89'),
            (True, True, '2001:0123:4567:89ab:cdef:ABCD:EFAB:CDEF'),
            (True, True, '[2001:abc::1234]'),
        ]
    )
    def test_validate_hostname_valid(require_tld, allow_ip, input_string):
        """ Test validate_hostname() with different options and valid input strings. """
        assert internet_helpers.validate_hostname(input_string, require_tld=require_tld, allow_ip=allow_ip) is True

    @staticmethod
    @pytest.mark.parametrize(
        'require_tld, allow_ip, input_string', [
            # Nonsense input
            (True, True, ''),
            (False, True, ''),
            (False, True, '[]'),
            (False, True, '$example.com'),

            # TLD required
            (True, True, 'example'),

            # IP addresses not allowed
            (True, False, '123.45.67.78'),
            (False, False, '123.45.67.78'),
            (True, False, '2001:abc::1234'),
            (False, False, '[2001:abc::1234]'),
        ]
    )
    def test_validate_hostname_invalid(require_tld, allow_ip, input_string):
        """ Test validate_hostname() with different options and invalid input strings. """
        assert internet_helpers.validate_hostname(input_string, require_tld=require_tld, allow_ip=allow_ip) is False

    # Tests for validate_ip_address()

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # IPv4 addresses
            '1.1.1.1',
            '127.0.0.1',
            '123.45.67.89',
            '255.255.255.254',
            # IPv6 addresses (full representation)
            '2001:0000:0000:0000:0000:0000:0000:0001',
            '2001:0123:4567:89ab:cdef:ABCD:EFAB:CDEF',
            # IPv6 addresses (shortened)
            '2001::1',
            '2001:abc::1234',
        ]
    )
    def test_validate_ip_address_valid(input_string):
        """ Test validate_ip_address() with valid IP address strings. """
        assert internet_helpers.validate_ip_address(input_string) is True

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Nonsense input
            '',
            'banana',
            # Invalid IPv4 addresses
            '1.2.3.256',
            '256.0.0.1',
            '123.45.67',
            'a.b.c.d',
            # Invalid IPv6 addresses
            '2001:0000:0000:0000:0000:0000:0000:0000:0001',
            '2001:0123:4567:89ab:cdef:xxxx:xxxx:xxxx',
            '2001:1',
        ]
    )
    def test_validate_ip_address_invalid(input_string):
        """ Test validate_ip_address() with invalid input strings. """
        assert internet_helpers.validate_ip_address(input_string) is False

    # Tests for validate_domain_name()

    @staticmethod
    @pytest.mark.parametrize(
        'require_tld, input_string', [
            # Don't require TLD
            (False, 'example'),
            (False, 'example.com'),
            (False, 'foo-123-bar'),
            # Require TLD
            (True, 'example.com'),
            (True, '123.sub.sub.sub.domain.Example.COM'),
            (True, 'xn--hxajbheg2az3al.xn--qxam'),
            # Domain labels may be up to 63 characters long
            (False, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com'),  # 63x 'a'
            # Total domain name may be up to 253 characters long
            (False, ('a.' * 126) + 'a'),
        ]
    )
    def test_validate_domain_name_valid(require_tld, input_string):
        """ Test validate_domain_name() with valid domain name strings. """
        assert internet_helpers.validate_domain_name(input_string, require_tld=require_tld) is True

    @staticmethod
    @pytest.mark.parametrize(
        'require_tld, input_string', [
            # Empty strings
            (True, ''),
            (False, ''),
            # Invalid characters
            (False, '$example.com'),
            (False, 'foo.-'),
            (False, '-foo.com'),
            (False, 'foo-.com'),
            # TLD required
            (True, 'foo-bar'),
            # Domain labels may not be longer than 63 characters
            (False, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com'),  # 64x 'a'
            # Total domain name may not be longer than 253 characters
            (False, ('a.' * 126) + 'aa'),
        ]
    )
    def test_validate_domain_name_invalid(require_tld, input_string):
        """ Test validate_domain_name() with invalid input strings. """
        assert internet_helpers.validate_domain_name(input_string, require_tld=require_tld) is False
