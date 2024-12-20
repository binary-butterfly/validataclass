"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import decimal
import math
from decimal import Decimal
from typing import Any

from validataclass.exceptions import NonFiniteNumberError
from .decimal_validator import DecimalValidator

__all__ = [
    'FloatToDecimalValidator',
]


class FloatToDecimalValidator(DecimalValidator):
    """
    Validator that converts float values (IEEE 754) to `decimal.Decimal` objects. Sub class of `DecimalValidator`.

    Optionally the parameters `min_value` and `max_value` (allowed number range), `output_places` (fixed number of
    decimal places in the output value) and `rounding` (rounding mode as defined in the `decimal` module) can be
    specified, which will be passed to the underlying `DecimalValidator`.

    By default, only floats are allowed as input type. Set `allow_integers=True` to also accept integers as input (e.g.
    `1` results in a `Decimal('1')`). Furthermore, with `allow_strings=True` the validator will also accept decimal
    strings exactly like the `DecimalValidator` (e.g. `"1.23"` results in a `Decimal('1.23')`).

    NOTE: Due to the way that floats work, the resulting decimals can have inaccuracies! It is recommended to use
    `DecimalValidator` with decimal *strings* as input data instead of using float input (e.g. strings like `"1.234"`
    instead of floats like `1.234`). This validator mainly exists for cases where you need to accept floats as input
    (e.g. with APIs that you have no control over).

    Examples:

    ```
    # Allows any (finite) float value, e.g. 1.234 -> Decimal('1.234')
    FloatToDecimalValidator()

    # Accepts integers as input, e.g. 123 -> Decimal('123')
    FloatToDecimalValidator(allow_integers=True)

    # Accepts strings as input, e.g. "1.23" -> Decimal('1.23')
    FloatToDecimalValidator(allow_strings=True)

    # Only allow zero or positive numbers
    FloatToDecimalValidator(min_value=0)

    # Only allow values from -0.5 to 0.5
    FloatToDecimalValidator(min_value='-0.5', max_value='0.5')

    # Set fixed number of output decimal places (e.g. 1.0 -> '1.00', 1.2345 -> 1.23, 1.999 -> '2.00')
    FloatToDecimalValidator(output_places=2)
    ```

    Valid input: `float` (also `int` if `allow_integers=True`; also `str` if `allow_strings=True`)
    Output: `decimal.Decimal`
    """

    # Whether to allow integers and/or decimal strings as input
    allow_integers: bool = False
    allow_strings: bool = False

    # List of allowed input types
    allowed_types: list[type]

    def __init__(
        self,
        *,
        min_value: Decimal | str | float | int | None = None,
        max_value: Decimal | str | float | int | None = None,
        output_places: int | None = None,
        rounding: str | None = decimal.ROUND_HALF_UP,
        allow_integers: bool = False,
        allow_strings: bool = False,
    ):
        """
        Creates a `FloatToDecimalValidator` with optional value range and number of output decimal places.

        The parameters `min_value`, `max_value`, `output_places` and `rounding` are passed to the underlying
        `DecimalValidator`.

        The parameters `allow_integers` and `allow_strings` can be used to extend the allowed input types. If strings
        are accepted, they will be simply passed to the `DecimalValidator`.

        Parameters:
            `min_value`: Decimal, str, float or int, specifies lowest allowed value (default: `None`, no minimum)
            `max_value`: Decimal, str, float or int, specifies highest allowed value (default: `None`, no maximum)
            `output_places`: Integer, if set, values are rounded to this number of decimal places (default: `None`)
            `rounding`: Rounding mode for numbers that need to be rounded (default: `decimal.ROUND_HALF_UP`)
            `allow_integers`: Boolean, whether to accept integers as input (default: False)
            `allow_strings`: Boolean, whether to accept and parse decimal strings (default: False)
        """
        # Initialize base DecimalValidator
        super().__init__(
            min_value=str(min_value) if isinstance(min_value, float) else min_value,
            max_value=str(max_value) if isinstance(max_value, float) else max_value,
            output_places=output_places,
            rounding=rounding,
        )

        # Save parameters
        self.allow_integers = allow_integers
        self.allow_strings = allow_strings

        # Prepare list of allowed input types
        self.allowed_types = [float]
        if allow_integers:
            self.allowed_types.append(int)
        if allow_strings:
            self.allowed_types.append(str)

    def validate(self, input_data: Any, **kwargs: Any) -> Decimal:  # type: ignore[override]
        """
        Validates input data as a float (optionally also as integer or string), then converts it to a `Decimal` object.
        """
        # Check type of input data
        self._ensure_type(input_data, self.allowed_types)

        # In case of floats, ensure the value is finite (i.e. neither Infinity nor NaN)
        if type(input_data) is float and not math.isfinite(input_data):
            raise NonFiniteNumberError()

        # Convert floats and integers to decimal strings first
        input_str = str(input_data)

        # Parse decimal strings using the base DecimalValidator
        return super().validate(input_str, **kwargs)
