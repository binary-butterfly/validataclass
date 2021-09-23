# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from typing import Any, Optional, List

from .string_validator import StringValidator
from wtfjson.exceptions import InvalidUrlError
from wtfjson.internal import internet_helpers

__all__ = [
    'UrlValidator',
]


class UrlValidator(StringValidator):
    """
    Validator that parses URLs. Valid URLs are returned unmodified.

    Please note that this validator is a bit opinionated and simplified in that it does *not* allow every valid URL. It's intended to be
    used primarily for HTTP URLs and thus only allows URLs with authority component (the "//host" part after the colon).

    By default the validator allows only the URI schemes "http" and "https". This can be changed by setting the parameter 'allowed_schemes'
    to a list of strings. To allow arbitrary (but valid) URI schemes, use the empty list (e.g. `allowed_schemes=[]`). Schemes are checked
    case-insensitive, e.g. "https://..." and "HTTPS://..." are equivalent (the output string will be unmodified though).

    Additionally the following boolean parameters can be used to specify further validation options:

    - require_tld: Whether hostnames are required to have a top level domain (e.g. "example.com" but not "example"; default: True)
    - allow_ip: Whether IP addresses are allowed as hosts (e.g. "https://1.2.3.4/foo" or "https://[2001:abc::1]/foo"; default: True)
    - allow_userinfo: Whether the URL may have a userinfo component (e.g. "https://username:password@example.com"; default: False)

    Examples:

    ```
    # Default options: Only allows "http(s)" as scheme, requires a TLD, allows IP, does not allow userinfo.
    #   Valid: "https://example.com", "http://123.45.67.89/foo", "http://example.com:8080/foo?bar=baz#bloop"
    #   Invalid: "ftp://example.com", "http://localhost", "https://username@example.com"
    UrlValidator()

    # Set allowed_schemes to allow only "ftp" and "sftp", also allow userinfo
    #   Valid: "ftp://example.com/foo/bar", "sftp://username:password@example.com/foo/bar"
    #   Invalid: any URL with a different scheme
    UrlValidator(allowed_schemes=['ftp', 'sftp], allow_userinfo=True)

    # Allow arbitrary schemes (as long as they are valid, i.e. only consist of the characters a-z, 0-9, ".+-" and start with a letter)
    #   Valid: "https://example.com", "foo+bar-baz://example.com"
    #   Invalid: "://example.com", "-foo://example.com"
    UrlValidator(allowed_schemes=[])

    # Do not require a host with TLD (e.g. "http://localhost" would be valid now)
    UrlValidator(require_tld=False)

    # Do not allow IP addresses as host (e.g. "https://1.2.3.4/foo" would be invalid)
    UrlValidator(allow_ip=False)
    ```

    Valid input: URLs as `str`
    Output: `str`
    """

    # List of schemes allowed in URLs (empty list means any scheme is allowed)
    allowed_schemes: List[str]

    # Whether domain names must have a top-level domain (e.g. "myhost" or "localhost" would not be allowed)
    require_tld: bool

    # Whether IP addresses are allowed instead of a hostname
    allow_ip: bool

    # Whether the URL may contain the userinfo subcomponent (e.g. "https//userinfo@host/...")
    allow_userinfo: bool

    # Precompiled regular expression
    url_regex: re.Pattern = re.compile(r'''
        (?P<scheme> [a-z][a-z0-9.+-]* )
        ://
        ((?P<userinfo> [^@/?#\[\]]+ )@)?
        (?P<host> [^@:/?#\[\]]+ | \[[0-9a-f:]+] )
        (:(?P<port> [1-9][0-9]* ))?
        (?P<path_etc> [/?#] ([^%] | %[0-9a-f]{2})* )?
    ''', re.IGNORECASE | re.VERBOSE)

    def __init__(
        self, *,
        allowed_schemes: Optional[List[str]] = None,
        require_tld: bool = True,
        allow_ip: bool = True,
        allow_userinfo: bool = False,
    ):
        """
        Create a `UrlValidator` with optional parameters.

        Specify `allowed_schemes` to set a list of allowed URI schemes, which defaults to "http" and "https". As a special value, the
        empty list can be used to allow any valid schemes.

        Parameters:
            allowed_schemes: `list[str]`, specifies allowed URI schemes (default: `['http', 'https']`)
            require_tld: `bool`, whether hostnames must have a top level domain (default: True)
            allow_ip: `bool`, whether IP addresses are allowed as host (default: True)
            allow_userinfo: `bool`, whether URLs may contain userinfo (default: False)
        """
        # Initialize StringValidator with some length requirements
        super().__init__(min_length=1, max_length=2000)

        # Save allowed schemes
        if allowed_schemes is None:
            self.allowed_schemes = ['http', 'https']
        else:
            self.allowed_schemes = [scheme.lower() for scheme in allowed_schemes]

        # Save other parameters
        self.require_tld = require_tld
        self.allow_ip = allow_ip
        self.allow_userinfo = allow_userinfo

    def validate(self, input_data: Any) -> str:
        """
        Validate that input is a valid URL string. Returns unmodified string.
        """
        # Validate input data as string
        input_url = super().validate(input_data)

        # Validate string with regular expression
        regex_match = self.url_regex.fullmatch(input_url)
        if not regex_match:
            raise InvalidUrlError(reason='Invalid URL format.')

        # Check if scheme is in list of allowed schemes (empty list means all are allowed)
        url_scheme = regex_match.group('scheme').lower()
        if len(self.allowed_schemes) > 0 and url_scheme not in self.allowed_schemes:
            raise InvalidUrlError(reason='URL scheme is not allowed.')

        # Check if URL contains the userinfo subcomponent
        if not self.allow_userinfo and regex_match.group('userinfo') is not None:
            raise InvalidUrlError(reason='Userinfo component not allowed in URL.')

        # Validate host (domain or IP address)
        url_host = regex_match.group('host')
        if not internet_helpers.validate_hostname(url_host, require_tld=self.require_tld, allow_ip=self.allow_ip):
            raise InvalidUrlError(reason='Invalid host in URL.')

        # Validate port number
        url_port = regex_match.group('port')
        if url_port is not None and int(url_port) > 65535:
            raise InvalidUrlError(reason='Invalid port number in URL.')

        # URL is valid :)
        return input_url
