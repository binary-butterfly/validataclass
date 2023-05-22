"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import re
from typing import Any

from .string_validator import StringValidator
from validataclass.exceptions import InvalidEmailError
from validataclass.internal import internet_helpers

__all__ = [
    'EmailValidator',
]

# Helper variables to construct regular expressions
_REGEX_LOCAL_PART_CHARS = r"[a-z0-9!#$%&'*+\-/=?^_`{|}~]"


class EmailValidator(StringValidator):
    """
    Validator for email addresses.

    Please note that this validator is a bit opinionated and simplified in that it does *not* allow every email address
    that technically is valid according to the RFCs. For example, it does neither allow internationalized email
    addresses (although this might be changed in the future), nor oddities like quoted strings as local part or comments,
    because most mail software does not support those anyway and/or might break with those addresses.

    Set the parameter `allow_empty=True` to allow empty strings as input.

    To automatically convert the output email address to lowercase, you can set the parameter `to_lowercase=True`.

    By default, the maximum string length is set to 256 characters. This can be changed with the `max_length` parameter.

    Example:

    ```
    EmailValidator()

    # Accepts also empty strings
    EmailValidator(allow_empty=True)

    # Converts email addresses to lowercase (e.g. "Foo.Bar@Example.COM" -> "foo.bar@example.com")
    EmailValidator(to_lowercase=True)
    ```

    Valid input: email address as `str` (also empty strings if `allow_empty=True`)
    Output: `str`
    """

    # Precompiled regular expression
    email_regex: re.Pattern = re.compile(f'''
        (?P<local_part> {_REGEX_LOCAL_PART_CHARS}+ (?: \\.{_REGEX_LOCAL_PART_CHARS}+)* )
        @
        (?P<domain> [^@?]+ )
    ''', re.IGNORECASE | re.VERBOSE)

    # Whether to accept empty strings
    allow_empty: bool = False

    # Whether to automatically convert strings to lowercase
    to_lowercase: bool = False

    def __init__(
        self,
        *,
        allow_empty: bool = False,
        to_lowercase: bool = False,
        max_length: int = 256,
    ):
        """
        Create a `EmailValidator`.

        Parameters:
            allow_empty: Boolean, if True, empty strings are accepted as valid input (default: False)
            to_lowercase: Boolean, if True, the output will be automatically converted to lowercase (default: False)
            max_length: Integer, maximum length of input string (default: 256)
        """
        # Initialize StringValidator with some length requirements
        super().__init__(
            min_length=0 if allow_empty else 1,
            max_length=max_length,
        )

        # Save parameters
        self.allow_empty = allow_empty
        self.to_lowercase = to_lowercase

    def validate(self, input_data: Any, **kwargs) -> str:
        """
        Validate that input is a valid email address string. Returns unmodified string.
        """
        # Validate input data as string
        input_email = super().validate(input_data, **kwargs)

        # Allow empty strings (also strings consisting only of spaces) if `allow_empty=True`
        if self.allow_empty and input_email == "":
            return input_email

        # Validate string with regular expression
        regex_match = self.email_regex.fullmatch(input_email)
        if not regex_match:
            raise InvalidEmailError(reason='Invalid email address format.')

        # Check length of local part
        local_part = regex_match.group('local_part')
        if len(local_part) > 64:
            raise InvalidEmailError(reason='Local part is too long.')

        # Validate domain
        email_domain = regex_match.group('domain')
        if not internet_helpers.validate_domain_name(email_domain, require_tld=True):
            raise InvalidEmailError(reason='Domain not valid.')

        # Convert to lowercase (if enabled)
        if self.to_lowercase:
            input_email = input_email.lower()

        # Email address is valid :)
        return input_email
