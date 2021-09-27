# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from typing import Any, Optional, Union

from .string_validator import StringValidator
from wtfjson.exceptions import RegexMatchError

__all__ = [
    'RegexValidator',
]


class RegexValidator(StringValidator):
    """
    Validator that matches strings against a specified regular expression, optionally with minimal/maximal length requirements.

    This validator is based on the `StringValidator` which first handles type checking and optional length requirements.
    The input string is then matched against the regex using `re.fullmatch()` from the Python standard library, which means that the
    *full* string must match the regex.

    The regex can be specified either as a precompiled pattern (see `re.compile()`) or as a string which will be compiled by the class.
    Regex flags (e.g. `re.IGNORECASE` for case-insensitive matching) can only be set by precompiling a pattern with those flags.

    For further information on regular expressions, see: https://docs.python.org/3/library/re.html

    If the input string does not match the regex, a `RegexMatchError` validation error with the error code 'invalid_string_format' is
    raised. The error code can be overridden with the 'custom_error_code' parameter to get more explicit error messages.

    By default only "safe" singleline strings are allowed (i.e. no non-printable characters). See the `StringValidator` options 'unsafe'
    and 'multiline' for more details.

    Examples:

    ```
    # Import Python standard library for regular expressions
    import re

    # Use a precompiled regular expression to match lower-case hexadecimal numbers (e.g. '0', '123abc', '00ff00')
    RegexValidator(re.compile(r'[0-9a-f]+'))

    # Same as above, but with the re.IGNORECASE flag for case-insensitive matching (e.g. '123abc', '123ABC')
    RegexValidator(re.compile(r'[0-9a-f]+', re.IGNORECASE))

    # Same as above, but using a raw string instead of a precompiled pattern (explicitly allowing uppercase letters in character class)
    RegexValidator(r'[0-9a-fA-F]+')

    # As above, but setting string length requirements to only allow 6-digit hex numbers (e.g. '123abc')
    RegexValidator(re.compile(r'[0-9a-f]+', re.IGNORECASE), min_length=6, max_length=6)

    # Set a custom error code (on error, validator will raise RegexMatchError with dict representation {'code': 'invalid_hex_number'})
    RegexValidator(re.compile(r'[0-9a-f]+'), custom_error_code='invalid_hex_number')
    ```

    Valid input: Any `str` that matches the regex
    Output: `str` (unmodified input if valid)
    """

    # Precompiled regex pattern
    regex_pattern: re.Pattern

    # Error code to use in RegexMatchError exception (use default if None)
    custom_error_code: Optional[str] = None

    def __init__(self, pattern: Union[re.Pattern, str], *, custom_error_code: Optional[str] = None, **kwargs):
        """
        Create a RegexValidator with a specified regex pattern (as string or precompiled `re.Pattern` object).

        Optionally with a custom error code. Other keyword arguments (e.g. 'min_length', 'max_length', 'multiline' and 'unsafe') will be
        passed to `StringValidator`.
        """
        # Initialize base StringValidator (may set min_length/max_length via kwargs)
        super().__init__(**kwargs)

        # Save regex pattern (precompile if necessary)
        if isinstance(pattern, re.Pattern):
            self.regex_pattern = pattern
        else:
            self.regex_pattern = re.compile(pattern)

        # Save custom error code
        if custom_error_code is not None:
            self.custom_error_code = custom_error_code

    def validate(self, input_data: Any) -> str:
        """
        Validate input as string and match full string against regular expression. Returns unmodified string.
        """
        # Validate input with base StringValidator (checks length requirements)
        input_data = super().validate(input_data)

        # Match full string against Regex pattern
        if not self.regex_pattern.fullmatch(input_data):
            raise RegexMatchError(code=self.custom_error_code)

        return input_data
