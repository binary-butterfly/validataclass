# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from .validator import Validator
from wtfjson.exceptions import StringTooShortError, StringTooLongError, StringInvalidCharactersError, InvalidValidatorOptionException

__all__ = [
    'StringValidator',
]


class StringValidator(Validator):
    """
    Validator for arbitrary strings, optionally with minimal/maximal length requirements.

    By default only "safe" singleline strings are allowed, i.e. strings are not allowed to contain non-printable characters (like
    newlines or ASCII control characters, see https://docs.python.org/3/library/stdtypes.html#str.isprintable). The 'unsafe' option can
    be set to True to allow non-printable characters (with the exception of newlines, see next paragraph). Please make sure to handle
    such unsafe strings properly after validation though.

    To allow multiline strings (i.e. strings that contain the newline characters '\n' and/or '\r'), the 'multiline' option can be set
    to True. This is also necessary in unsafe mode, so setting `unsafe=True` alone will only allow *most* non-printable characters, but
    still no '\n' or '\r'. To allow unsafe multiline strings, you need to set `unsafe=True, multiline=True`.

    In safe mode (default), line endings in multiline strings will be normalized to Unix line endings (thus, "\r\n" and "\r" are allowed
    as line endings and will be converted to "\n"). In *unsafe* mode, line endings will be preserved as they are in the input string.

    Examples:

    ```
    # Accepts any safe singleline string (no newlines or other control characters) of any length
    StringValidator()

    # Restricts input to strings that have a length of at least one character
    StringValidator(min_length=1)

    # Restricts input to strings that have a length of at least one, but at most 200 characters
    StringValidator(min_length=1, max_length=200)

    # Accepts safe multiline strings of any length, normalizing line endings (e.g. "foo\r\nbar\rbaz\n" will result in "foo\nbar\nbaz\n")
    StringValidator(multiline=True)

    # Accepts unsafe strings, but only singlelined (e.g. "foo\0bar" will be allowed, but "foo\nbar" or "foo\rbar" will not)
    StringValidator(unsafe=True)

    # Accepts unsafe multiline strings, thus allowing *every* possible ASCII or UTF-8 character
    StringValidator(multiline=True, unsafe=True)
    ```

    Valid input: `str`
    Output: `str`
    """

    # Length constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    # Whether or not to allow multiline strings (i.e. strings containing newlines)
    allow_multiline: bool = False

    # Whether or not to allow "unsafe" strings (i.e. strings with non-printable characters)
    unsafe: bool = False

    def __init__(
        self, *,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        multiline: bool = False,
        unsafe: bool = False,
    ):
        """
        Create a StringValidator with optional length requirements and other options.

        By default, strings with non-printable characters, including newlines, are not allowed. This can be changed using the parameters
        'multiline' and 'unsafe'. See class description for details.

        Parameters:
            min_length: `int`, specifies minimum length of input strings (default: None, no minimum length)
            max_length: `int`, specifies maximum length of input strings (default: None, no maximum length)
            multiline: `bool`, whether to allow newlines in strings (default: False)
            unsafe: `bool`, whether to allow non-printable characters (except for newlines, see 'multiline') in strings (default: False)
        """
        # Check parameter validity
        if min_length is not None and min_length < 0:
            raise InvalidValidatorOptionException('Parameter "min_length" cannot be negative.')
        if max_length is not None and max_length < 0:
            raise InvalidValidatorOptionException('Parameter "max_length" cannot be negative.')
        if min_length is not None and max_length is not None and min_length > max_length:
            raise InvalidValidatorOptionException('Parameter "min_length" cannot be greater than "max_length".')

        # Save parameters
        self.min_length = min_length
        self.max_length = max_length
        self.allow_multiline = multiline
        self.unsafe = unsafe

    def validate(self, input_data: Any) -> str:
        """
        Validate input data to be a valid string, optionally checking length and allowed characters.

        Returns the input string with normalized line endings (only in safe multiline mode).
        """
        self._ensure_type(input_data, str)

        # Cast to string (for type hinting)
        input_str = str(input_data)

        # Check length
        if self.min_length is not None and len(input_str) < self.min_length:
            raise StringTooShortError(min_length=self.min_length, max_length=self.max_length)
        if self.max_length is not None and len(input_str) > self.max_length:
            raise StringTooLongError(min_length=self.min_length, max_length=self.max_length)

        # Check string for non-printable characters, unless in unsafe mode
        if not self.unsafe:
            # Temporarily replace newline characters (\n and \r) because those are non-printable and will be checked later
            input_without_newlines = input_str.translate({10: ' ', 13: ' '})
            if not input_without_newlines.isprintable():
                raise StringInvalidCharactersError(reason='String contains non-printable characters.')

        # Check if the string contains newlines
        if '\n' in input_str or '\r' in input_str:
            if not self.allow_multiline:
                raise StringInvalidCharactersError(reason='No multiline strings allowed.')

            # Normalize newlines (replace '\r\n' and '\r' with '\n'), unless in unsafe mode
            if not self.unsafe:
                input_str = input_str.replace('\r\n', '\n').replace('\r', '\n')

        return input_str
