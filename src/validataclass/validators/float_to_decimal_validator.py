"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import math
from decimal import Decimal
from typing import Any, Optional, Union, List

from validataclass.exceptions import NonFiniteNumberError
from .decimal_validator import DecimalValidator

__all__ = [
    'FloatToDecimalValidator',
]


class FloatToDecimalValidator(DecimalValidator):
    """
    Validator that converts float values (IEEE 754) to `decimal.Decimal` objects. Sub class of `DecimalValidator`.

    Optionally a number range can be specified using the parameters 'min_value' and 'max_value' (specified as `Decimal`,
    decimal strings, floats or integers), as well as a fixed number of decimal places in the output value using
    'output_places'. These parameters will be passed to the underlying `DecimalValidator`.

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
    allowed_types: List[type]

    def __init__(
        self, *,
        min_value: Optional[Union[Decimal, str, float, int]] = None,
        max_value: Optional[Union[Decimal, str, float, int]] = None,
        output_places: Optional[int] = None,
        allow_integers: bool = False,
        allow_strings: bool = False,
    ):
        """
        Create a FloatToDecimalValidator with optional value range and optional number of decimal places in output value.

        The parameters 'min_value', 'max_value' and 'output_places' are passed to the underlying DecimalValidator.

        The parameters 'allow_integers' and 'allow_strings' can be used to extend the allowed input types. Strings, if
        accepted, will be simply passed to the DecimalValidator.

        Parameters:
            min_value: Decimal, str, float or int, specifies lowest value an input float may have (default: None, no minimum value)
            max_value: Decimal, str, float or int, specifies highest value an input float may have (default: None, no maximum value)
            output_places: Integer, number of decimal places the output Decimal object shall have (default: None, output equals input)
            allow_integers: Boolean, if True, integers are accepted as input (default: False)
            allow_strings: Boolean, if True, decimal strings are accepted and will be parsed by a DecimalValidator (default: False)
        """
        # Initialize base DecimalValidator
        super().__init__(
            min_value=str(min_value) if type(min_value) in [float, int] else min_value,
            max_value=str(max_value) if type(max_value) in [float, int] else max_value,
            output_places=output_places,
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

    def validate(self, input_data: Any) -> Decimal:
        """
        Validate input data as a float (optionally also as integer or string), then convert it to a Decimal object.
        """
        # Check type of input data
        self._ensure_type(input_data, self.allowed_types)

        # In case of floats, ensure the value is finite (i.e. neither Infinity nor NaN)
        if type(input_data) is float and not math.isfinite(input_data):
            raise NonFiniteNumberError()

        # Convert floats and integers to decimal strings first
        input_str = str(input_data)

        # Parse decimal strings using the base DecimalValidator
        return super().validate(input_str)
