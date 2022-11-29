"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import decimal
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Union

from validataclass.exceptions import InvalidDecimalError, NumberRangeError, DecimalPlacesError, InvalidValidatorOptionException
from .string_validator import StringValidator

__all__ = [
    'DecimalValidator',
]


class DecimalValidator(StringValidator):
    """
    Validator that parses decimal numbers from strings (e.g. '1.234') to `decimal.Decimal` objects.

    Only allows finite numbers in regular decimal notation (e.g. '1.234', '-42', '.00', ...), but no other values that
    are accepted by `decimal.Decimal` (e.g. no 'Infinity' or 'NaN' and no scientific notation).

    Optionally a number range (minimum/maximum value as `Decimal`, integer or decimal string) can be specified using the
    parameters `min_value` and `max_value`, as well as a minimum/maximum number of decimal places in the input using
    `min_places` and `max_places`.

    You can also specify how many decimal places the output value should have using `output_places`. If this parameter
    is set, the output value will always have the specified amount of decimal places. If rounding is necessary, a
    rounding mode as defined by the `decimal` module (https://docs.python.org/3/library/decimal.html#rounding-modes) is
    used, which can be specified with the `rounding` parameter.

    The rounding mode defaults to `decimal.ROUND_HALF_UP`, which basically means that digits 0 to 4 are rounded down and
    digits 5 to 9 are rounded up (e.g. with `output_places=1`, "1.149" would be rounded to "1.1" and "1.150" would be
    rounded to "1.2"). Alternatively, set `rounding=None` to use the rounding mode set by the current decimal context.

    Examples:

    ```
    # No constraints
    DecimalValidator()

    # Only allow zero or positive numbers (e.g. '0', '0.000', '1.234', but not '-0.001' or other negative numbers)
    DecimalValidator(min_value=0)

    # Only allow values from -0.5 to 0.5, including the boundaries (e.g. '0.5', '-0.123', but not '0.501')
    DecimalValidator(min_value='-0.5', max_value='0.5')

    # Allow any value with 2 or 3 decimal places (e.g. '0.123', '-123456.00', but not '0.1' or '0.1234')
    DecimalValidator(min_places=2, max_places=3)

    # No constraints, but output Decimal will always have 2 places (e.g. '1' -> '1.00', '1.2345' -> '1.23', '1.999' -> '2.00')
    DecimalValidator(output_places=2)

    # As above, but only allow 2 or less decimal places in input (e.g. '1' -> '1.00', '1.23' -> '1.23' but '1.234' raises an exception)
    DecimalValidator(max_places=2, output_places=2)

    # Two output places, but always round up (e.g. '1.001' -> '1.01')
    DecimalValidator(output_places=2, rounding=decimal.ROUND_UP)
    ```

    Valid input: `str` in decimal notation
    Output: `decimal.Decimal`
    """

    # Value constraints
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None

    # Minimum/maximum number of decimal places
    min_places: Optional[int] = None
    max_places: Optional[int] = None

    # Quantum used in `.quantize()` to set a fixed number of decimal places (from constructor argument output_places)
    output_quantum: Optional[Decimal] = None

    # Rounding mode (constant from decimal module)
    rounding: Optional[str] = None

    # Precompiled regular expression for decimal values
    decimal_regex: re.Pattern = re.compile(r'[+-]?([0-9]+\.[0-9]*|\.?[0-9]+)')

    def __init__(
        self, *,
        min_value: Optional[Union[Decimal, int, str]] = None,
        max_value: Optional[Union[Decimal, int, str]] = None,
        min_places: Optional[int] = None,
        max_places: Optional[int] = None,
        output_places: Optional[int] = None,
        rounding: Optional[str] = decimal.ROUND_HALF_UP,
    ):
        """
        Create a DecimalValidator with optional value range, optional minimum/maximum number of decimal places and
        optional number of decimal places in output value.

        Parameters:
            min_value: Decimal, integer or string, specifies lowest allowed value (default: None, no minimum value)
            max_value: Decimal, integer or string, specifies highest allowed value (default: None, no maximum value)
            min_places: Integer, minimum number of decimal places an input value must have (default: None, no minimum places)
            max_places: Integer, maximum number of decimal places an input value must have (default: None, no maximum places)
            output_places: Integer, number of decimal places the output Decimal object shall have (default: None, output equals input)
            rounding: Rounding mode for numbers that need to be rounded (default: decimal.ROUND_HALF_UP)
        """
        # Restrict string length
        super().__init__(max_length=40)

        # Convert min_value/max_value from strings or integers to Decimals if necessary
        if min_value is not None and not isinstance(min_value, Decimal):
            min_value = Decimal(min_value)
        if max_value is not None and not isinstance(max_value, Decimal):
            max_value = Decimal(max_value)

        # Check parameter validity
        if min_value is not None and max_value is not None and min_value > max_value:
            raise InvalidValidatorOptionException('Parameter "min_value" cannot be greater than "max_value".')

        if min_places is not None and min_places < 0:
            raise InvalidValidatorOptionException('Parameter "min_places" cannot be negative.')
        if max_places is not None and max_places < 0:
            raise InvalidValidatorOptionException('Parameter "max_places" cannot be negative.')
        if min_places is not None and max_places is not None and min_places > max_places:
            raise InvalidValidatorOptionException('Parameter "min_places" cannot be greater than "max_places".')

        # Save parameters
        self.min_value = min_value
        self.max_value = max_value
        self.min_places = min_places
        self.max_places = max_places
        self.rounding = rounding

        # Set output "quantum" (the output decimal will have the same number of decimal places as this value)
        if output_places is not None:
            if output_places < 0:
                raise InvalidValidatorOptionException('Parameter "output_places" cannot be negative.')
            self.output_quantum = Decimal('0.1') ** output_places

    def validate(self, input_data: Any, **kwargs) -> Decimal:
        """
        Validate input data as a string, convert it to a Decimal object and check optional constraints.
        """
        # First, validate input data as string
        decimal_string = super().validate(input_data, **kwargs)

        # Validate string with a regular expression
        if not self.decimal_regex.fullmatch(decimal_string):
            raise InvalidDecimalError()

        # Count decimal places
        places = len(decimal_string.rsplit('.', maxsplit=1)[1]) if '.' in decimal_string else 0

        # Validate number of decimal places
        if (self.min_places is not None and places < self.min_places) or (self.max_places is not None and places > self.max_places):
            raise DecimalPlacesError(min_places=self.min_places, max_places=self.max_places)

        # Try to parse string as decimal value
        try:
            decimal_out = Decimal(decimal_string)
        except InvalidOperation:  # pragma: nocover
            raise InvalidDecimalError()

        # Check if value is in allowed range
        if (self.min_value is not None and decimal_out < self.min_value) or (self.max_value is not None and decimal_out > self.max_value):
            min_value_str = str(self.min_value) if self.min_value is not None else None
            max_value_str = str(self.max_value) if self.max_value is not None else None
            raise NumberRangeError(min_value=min_value_str, max_value=max_value_str)

        # Set fixed number of decimal places (if wanted)
        if self.output_quantum is not None:
            return decimal_out.quantize(self.output_quantum, rounding=self.rounding)
        else:
            return decimal_out
