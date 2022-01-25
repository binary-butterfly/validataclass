"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import math
from typing import Any, Optional, Union

from .validator import Validator
from validataclass.exceptions import InvalidValidatorOptionException, NumberRangeError, NonFiniteNumberError

__all__ = [
    'FloatValidator',
]


class FloatValidator(Validator):
    """
    Validator for float values (IEEE 754), optionally with value range requirements.

    By default, input values must be of type `float`, so integers like `123` will not be accepted. Set the parameter
    `allow_integers=True` to allow integers as well and convert them to floats, e.g. the integer `123` would be converted
    to the float `123.0`.

    Only allows finite value (i.e. neither Infinity nor NaN).

    Examples:

    ```
    # Allows any (finite) float value, e.g. 1.234, -0.123, 0.0
    FloatValidator()

    # Accepts integers as input, e.g. 123 would be converted to 123.0
    FloatValidator(allow_integers=True)

    # Only allow zero or positive numbers
    FloatValidator(min_value=0)

    # Only allow values from -0.5 to 0.5
    FloatValidator(min_value=-0.5, max_value=0.5)
    ```

    Note: While it is allowed to set `max_value` without setting `min_value`, this might not do what you expect. For example,
    a `FloatValidator(max_value=10)` allows all values less than or equal to 10. This includes ANY negative number though, so
    for example `-12345.67` would be valid input!

    Valid input: `float` (also `int` if `allow_integers=True`)
    Output: `float`
    """

    # Value constraints
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    # Whether to accept integers and convert them to floats
    allow_integers: bool = False

    def __init__(
        self, *,
        min_value: Optional[Union[float, int]] = None,
        max_value: Optional[Union[float, int]] = None,
        allow_integers: bool = False,
    ):
        """
        Create a FloatValidator with optional value range.

        Parameters:
            min_value: Float or integer, specifies lowest value an input float may have (default: None, no minimum value)
            max_value: Float or integer, specifies highest value an input float may have (default: None, no maximum value)
            allow_integers: Boolean, if True, integers are accepted and converted to floats (default: False)
        """
        # Check parameter validity
        if min_value is not None and max_value is not None and min_value > max_value:
            raise InvalidValidatorOptionException('Parameter "min_value" cannot be greater than "max_value".')

        self.min_value = float(min_value) if min_value is not None else None
        self.max_value = float(max_value) if max_value is not None else None
        self.allow_integers = allow_integers

    def validate(self, input_data: Any) -> float:
        """
        Validate type (and optionally value) of input data. Returns unmodified float.
        """
        self._ensure_type(input_data, [float, int] if self.allow_integers else float)

        # If allow_integers is True, integers must be converted to floats
        input_float = float(input_data)

        # Ensure float is finite (i.e. neither Infinity nor NaN)
        if not math.isfinite(input_float):
            raise NonFiniteNumberError()

        # Check if value is in allowed range
        if (self.min_value is not None and input_float < self.min_value) or (self.max_value is not None and input_float > self.max_value):
            raise NumberRangeError(min_value=self.min_value, max_value=self.max_value)

        return input_float
