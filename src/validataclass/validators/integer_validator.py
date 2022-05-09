"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional

from .validator import Validator
from validataclass.exceptions import InvalidValidatorOptionException, InvalidIntegerError, NumberRangeError

__all__ = [
    'IntegerValidator',
]


class IntegerValidator(Validator):
    """
    Validator for integer values, optionally with value range requirements.

    Use the parameters `min_value` and/or `max_value` to set a value range (smallest and biggest allowed integer).
    By default, these parameters are set so that only 32 bit integers are allowed, i.e. only integers from -2147483648
    (-2^32) to 2147483647 (2^32 - 1).

    However, these are just default values. To allow integers outside the 32 bit range, set `min_value` and `max_value`
    to `None`.

    By default, only actual integer values (no strings) are allowed. Use the parameter `allow_strings=True` to allow
    numeric strings, e.g. the strings "-123" and "123" would be accepted and automatically converted to integers.

    Examples:

    ```
    # Accepts any 32 bit integer (e.g. -123456, 0, 123456, but not a string like "123")
    IntegerValidator()

    # Accepts any integer known to Python (e.g. -2147483649 and 2147483648, which would not be accepted by default)
    IntegerValidator(min_value=None, max_value=None)

    # Only accepts zero or positive numbers
    IntegerValidator(min_value=0)

    # Only accepts values 1 to 10 (including the numbers 1 and 10)
    IntegerValidator(min_value=1, max_value=10)

    # Accepts numeric strings, which will be converted to integers (e.g. "1234" -> 1234; "-123" -> -123)
    IntegerValidator(allow_strings=True)
    ```

    Note: While it is allowed to set `max_value` without setting `min_value`, this might not do what you expect. For example,
    an `IntegerValidator(max_value=10)` allows all values less than or equal to 10. This includes ANY negative number though,
    so for example `-1234567` would be valid input!

    Valid input: `int` (also `str` if `allow_strings=True`)
    Output: `int`
    """

    # Constants (minimum and maximum values for a 32 bit integer)
    DEFAULT_MIN_VALUE = -2147483648  # -2^32
    DEFAULT_MAX_VALUE = 2147483647  # 2^32 - 1

    # Value constraints
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    # Whether to allow integers as strings
    allow_strings: bool = False

    def __init__(
        self, *,
        min_value: Optional[int] = DEFAULT_MIN_VALUE,
        max_value: Optional[int] = DEFAULT_MAX_VALUE,
        allow_strings: bool = False,
    ):
        """
        Create a IntegerValidator with optional value range.

        Parameters:
            min_value: Integer or None, smallest allowed integer value (default: IntegerValidator.DEFAULT_MIN_VALUE = -2147483648)
            max_value: Integer or None, biggest allowed integer value (default: IntegerValidator.DEFAULT_MAX_VALUE = 2147483647)
            allow_strings: Boolean, if True, numeric strings (e.g. "123") are accepted and converted to integers (default: False)
        """
        # Check parameter validity
        if min_value is not None and max_value is not None and min_value > max_value:
            raise InvalidValidatorOptionException('Parameter "min_value" cannot be greater than "max_value".')

        self.min_value = min_value
        self.max_value = max_value
        self.allow_strings = allow_strings

    def validate(self, input_data: Any) -> int:
        """
        Validate type (and optionally value) of input data. Returns unmodified integer.
        """
        self._ensure_type(input_data, [int, str] if self.allow_strings else int)

        # If allow_strings is True, convert strings to integers
        if type(input_data) is str:
            try:
                input_data = int(input_data)
            except ValueError:
                raise InvalidIntegerError()

        # Check if value is in allowed range
        if (self.min_value is not None and input_data < self.min_value) or (self.max_value is not None and input_data > self.max_value):
            raise NumberRangeError(min_value=self.min_value, max_value=self.max_value)

        return int(input_data)
