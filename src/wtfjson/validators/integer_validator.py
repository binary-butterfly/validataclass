# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from .validator import Validator
from wtfjson.exceptions import InvalidValidatorOptionException, NumberRangeError

__all__ = [
    'IntegerValidator',
]


class IntegerValidator(Validator):
    """
    Validator for integer values, optionally with value range requirements.

    Examples:

    ```
    IntegerValidator()
    IntegerValidator(min_value=0)  # Only allow zero or positive numbers
    IntegerValidator(min_value=1, max_value=10)  # Only allow values 1 to 10 (including 1 and 10)
    ```

    Note: While it is allowed to set `max_value` without setting `min_value`, this might not do what you expect. For example,
    an `IntegerValidator(max_value=10)` allows all values less than or equal to 10. This includes ANY negative number though,
    so for example `-1234567` would be valid input!

    Valid input: `int`
    Output: `int`
    """

    # Value constraints
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    def __init__(self, *, min_value: Optional[int] = None, max_value: Optional[int] = None):
        """
        Create a IntegerValidator with optional value range.

        Parameters:
            min_value: Integer, specifies lowest value an input integer may have (default: None, no minimum value)
            max_value: Integer, specifies highest value an input integer may have (default: None, no maximum value)
        """
        # Check parameter validity
        if min_value is not None and max_value is not None and min_value > max_value:
            raise InvalidValidatorOptionException('Parameter "min_value" cannot be greater than "max_value".')

        self.min_value = min_value
        self.max_value = max_value

    def validate(self, input_data: Any) -> int:
        """
        Validate type (and optionally value) of input data. Returns unmodified integer.
        """
        self._ensure_type(input_data, int)

        # Check if value is in allowed range
        if (self.min_value is not None and input_data < self.min_value) or (self.max_value is not None and input_data > self.max_value):
            raise NumberRangeError(min_value=self.min_value, max_value=self.max_value)

        return int(input_data)
