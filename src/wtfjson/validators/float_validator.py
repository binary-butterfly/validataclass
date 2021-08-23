# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import math
from typing import Any, Optional, Union

from .validator import Validator
from wtfjson.exceptions import InvalidValidatorOptionException, NumberRangeError, NonFiniteNumberError

__all__ = [
    'FloatValidator',
]


class FloatValidator(Validator):
    """
    Validator for float values (IEEE 754), optionally with value range requirements.

    Only allows finite value (i.e. neither Infinity nor NaN).

    Examples:

    ```
    FloatValidator()

    # Only allow zero or positive numbers
    FloatValidator(min_value=0)

    # Only allow values from -0.5 to 0.5
    FloatValidator(min_value=-0.5, max_value=0.5)
    ```

    Note: While it is allowed to set `max_value` without setting `min_value`, this might not do what you expect. For example,
    a `FloatValidator(max_value=10)` allows all values less than or equal to 10. This includes ANY negative number though, so
    for example `-12345.67` would be valid input!

    Valid input: `float`
    Output: `float`
    """

    # Value constraints
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def __init__(self, *, min_value: Optional[Union[float, int]] = None, max_value: Optional[Union[float, int]] = None):
        """
        Create a FloatValidator with optional value range.

        Parameters:
            min_value: Float or integer, specifies lowest value an input float may have (default: None, no minimum value)
            max_value: Float or integer, specifies highest value an input float may have (default: None, no maximum value)
        """
        # Check parameter validity
        if min_value is not None and max_value is not None and min_value > max_value:
            raise InvalidValidatorOptionException('Parameter "min_value" cannot be greater than "max_value".')

        self.min_value = float(min_value) if min_value is not None else None
        self.max_value = float(max_value) if max_value is not None else None

    def validate(self, input_data: Any) -> float:
        """
        Validate type (and optionally value) of input data. Returns unmodified float.
        """
        self._ensure_type(input_data, float)

        # Ensure float is finite (i.e. neither Infinity nor NaN)
        if not math.isfinite(input_data):
            raise NonFiniteNumberError()

        # Check if value is in allowed range
        if (self.min_value is not None and input_data < self.min_value) or (self.max_value is not None and input_data > self.max_value):
            raise NumberRangeError(min_value=self.min_value, max_value=self.max_value)

        return float(input_data)
