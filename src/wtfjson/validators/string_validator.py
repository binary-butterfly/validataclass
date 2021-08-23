# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from .validator import Validator
from wtfjson.exceptions import StringTooShortError, StringTooLongError, InvalidValidatorOptionException

__all__ = [
    'StringValidator',
]


class StringValidator(Validator):
    """
    Validator for arbitrary strings, optionally with minimal/maximal length requirements.

    Examples:

    ```
    StringValidator()
    StringValidator(min_length=1)
    StringValidator(min_length=1, max_length=200)
    ```

    Valid input: `str`
    Output: `str`
    """

    # Length constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    def __init__(self, *, min_length: Optional[int] = None, max_length: Optional[int] = None):
        """
        Create a StringValidator with optional length requirements.

        Parameters:
            min_length: Integer, specifies minimum length of input strings (default: None, no minimum length)
            max_length: Integer, specifies maximum length of input strings (default: None, no maximum length)
        """
        # Check parameter validity
        if min_length is not None and min_length < 0:
            raise InvalidValidatorOptionException('Parameter "min_length" cannot be negative.')
        if max_length is not None and max_length < 0:
            raise InvalidValidatorOptionException('Parameter "max_length" cannot be negative.')
        if min_length is not None and max_length is not None and min_length > max_length:
            raise InvalidValidatorOptionException('Parameter "min_length" cannot be greater than "max_length".')

        self.min_length = min_length
        self.max_length = max_length

    def validate(self, input_data: Any) -> str:
        """
        Validate type (and optionally length) of input data. Returns unmodified string.
        """
        self._ensure_type(input_data, str)

        # Check length
        if self.min_length is not None and len(input_data) < self.min_length:
            raise StringTooShortError(min_length=self.min_length, max_length=self.max_length)
        if self.max_length is not None and len(input_data) > self.max_length:
            raise StringTooLongError(min_length=self.min_length, max_length=self.max_length)

        return str(input_data)
