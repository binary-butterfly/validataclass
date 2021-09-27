# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from typing import Any

from .string_validator import StringValidator
from wtfjson.exceptions import InvalidEmailError
from wtfjson.internal import internet_helpers

__all__ = [
    'EmailValidator',
]

# Helper variables to construct regular expressions
_REGEX_LOCAL_PART_CHARS = r"[a-z0-9!#$%&'*+\-/=?^_`{|}~]"


class EmailValidator(StringValidator):
    """
    Validator for email addresses.

    Please note that this validator is a bit opinionated and simplified in that it does *not* allow every email address that technically
    is valid according to the RFCs. For example, it does neither allow internationalized email addresses (although this might be changed
    in the future), nor oddities like quoted strings as local part or comments, because most mail software does not support those anyway
    and/or might break with those adresses.

    Currently this validator has no parameters.

    Example:

    ```
    EmailValidator()
    ```

    Valid input: email address as `str`
    Output: `str`
    """

    # Precompiled regular expression
    email_regex: re.Pattern = re.compile(f'''
        (?P<local_part> {_REGEX_LOCAL_PART_CHARS}+ (?: \\.{_REGEX_LOCAL_PART_CHARS}+)* )
        @
        (?P<domain> [^@?]+ )
    ''', re.IGNORECASE | re.VERBOSE)

    def __init__(self):
        """
        Create a `EmailValidator`.
        """
        # Initialize StringValidator with some length requirements
        super().__init__(min_length=1, max_length=256)

    def validate(self, input_data: Any) -> str:
        """
        Validate that input is a valid email address string. Returns unmodified string.
        """
        # Validate input data as string
        input_email = super().validate(input_data)

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

        # Email address is valid :)
        return input_email
