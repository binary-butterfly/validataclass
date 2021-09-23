# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import ipaddress
import re

__all__ = [
    'validate_hostname',
    'validate_ip_address',
    'validate_domain_name',
]

# Helper variables to construct regular expressions
_REGEX_DOMAIN_LABEL = r'([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)'

# Precompiled regular expressions
_ip_charset_regex: re.Pattern = re.compile(r'[0-9a-f.:\[\]]+', re.IGNORECASE)
_domain_optional_tld_regex: re.Pattern = re.compile(f'{_REGEX_DOMAIN_LABEL}(\\.{_REGEX_DOMAIN_LABEL})*', re.IGNORECASE)
_domain_required_tld_regex: re.Pattern = re.compile(f'{_REGEX_DOMAIN_LABEL}(\\.{_REGEX_DOMAIN_LABEL})+', re.IGNORECASE)


# Internal helper functions intended to be used by `UrlValidator`, `EmailValidator` and potentially other validators that work with
# network host identifiers, i.e. domain names and IP addresses.

def validate_hostname(hostname: str, *, require_tld: bool = False, allow_ip: bool = True) -> bool:
    """
    Checks whether a given string is a valid identifier for a network host, i.e. it is either a valid IP address (only if the
    `allow_ip` option is set) or a valid domain name.

    If `required_tld` is True, the domain name must also have an (arbitrary) top level domain to be considered valid, e.g.
    "foo.bar" is always valid, but "foobar" is only valid if `required_tld` is False.

    Parameters:
        hostname: `str`, input string to be validated
        require_tld: `bool`, specifies whether a domain name must have a top level domain (default: False)
        allow_ip: `bool`, specifies whether an IP address is considered a valid hostname (default: True)
    """
    # First check whether the string somewhat looks like an IP address (only contains characters allowed in IP addresses)
    if _ip_charset_regex.fullmatch(hostname):
        # Validate string as an IP address
        return validate_ip_address(hostname.strip('[]')) if allow_ip else False
    else:
        # Validate string as a domain name
        return validate_domain_name(hostname, require_tld=require_tld)


def validate_ip_address(ip_address: str) -> bool:
    """
    Checks whether a given string is a valid IP address (supports both IPv4 and IPv6).

    Parameters:
        ip_address: `str`, input string to be validated
    """
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def validate_domain_name(domain_name: str, *, require_tld: bool = False) -> bool:
    """
    Checks whether a given string is a valid domain name.

    If `required_tld` is True, the domain name must also have an (arbitrary) top level domain to be considered valid, e.g.
    "foo.bar" is always valid, but "foobar" is only valid if `required_tld` is False.

    Parameters:
        domain_name: `str`, input string to be validated
        require_tld: `bool`, specifies whether a domain name must have a top level domain (default: False)
    """
    # Check total length of domain name
    if len(domain_name) > 253:
        return False

    # Check domain name with regex (also checks that each label is 1 to 63 characters long)
    domain_regex = _domain_required_tld_regex if require_tld else _domain_optional_tld_regex
    return bool(domain_regex.fullmatch(domain_name))
