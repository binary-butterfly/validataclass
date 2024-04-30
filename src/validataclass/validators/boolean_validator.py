"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from validataclass.exceptions import InvalidTypeError
from .validator import Validator

__all__ = [
    'BooleanValidator',
]


class BooleanValidator(Validator):
    """
    Validator for boolean values (`True` and `False`).

    By default, input data must be of type `bool`. Optionally allows "boolean strings" (i.e. "true" and "false",
    case-insensitive), which will be converted to real booleans.

    Examples:

    ```
    # Only allows bool values True and False
    BooleanValidator()

    # Also allow strings "true" and "false" as input
    BooleanValidator(allow_strings=True)
    ```

    Valid input: `bool` (or `str` with certain values if `allow_strings=True`)
    Output: `bool`
    """

    # Whether the validator accepts strings like 'True' or 'False'
    allow_strings: bool = False

    def __init__(self, *, allow_strings: bool = False):
        """
        Creates a `BooleanValidator`, optionally allowing strings as input data.

        Parameters:
            `allow_strings`: Boolean, whether to allow the strings "true", "false" (default: `False`)
        """
        self.allow_strings = allow_strings

    def validate(self, input_data: Any, **kwargs: Any) -> bool:
        """
        Validates type of input data. Returns a boolean.
        """
        self._ensure_not_none(input_data)

        # Bools are returned immediately as they are
        if type(input_data) is bool:
            return input_data

        # Parse strings to booleans (if enabled)
        if self.allow_strings and type(input_data) is str:
            # Compare case-insensitively
            input_str = input_data.lower()

            # Check for valid boolean strings, or fallback to InvalidTypeError
            if input_str == 'true':
                return True
            elif input_str == 'false':
                return False

        raise InvalidTypeError(expected_types=bool)
