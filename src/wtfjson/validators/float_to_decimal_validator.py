# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Union

from .float_validator import FloatValidator
from wtfjson.exceptions import InvalidDecimalError, InvalidValidatorOptionException

__all__ = [
    'FloatToDecimalValidator',
]


class FloatToDecimalValidator(FloatValidator):
    """
    Validator that converts float values (IEEE 754) to `decimal.Decimal` objects. Superclass of `FloatValidator`.

    Optionally a number range (minimum/maximum float value) can be specified, which will be handled by the underlying FloatValidator.

    Also, similar to `DecimalValidator`, a fixed number of decimal places in the output value can be specified, which will result in
    rounding according to the current decimal context (see `decimal.getcontext()`).

    NOTE: Due to the way that floats work, the resulting decimals can have inaccuracies! It is recommended to use `DecimalValidator` with
    decimal *strings* as input data instead of using float input (e.g. strings like `"1.234"` instead of floats like `1.234`). This
    validator mainly exists for cases where you need to accept floats as input (e.g. with APIs that you have no control over).

    Examples:

    ```
    FloatToDecimalValidator()

    # Only allow zero or positive numbers
    FloatToDecimalValidator(min_value=0)

    # Only allow values from -0.5 to 0.5
    FloatToDecimalValidator(min_value=-0.5, max_value=0.5)

    # Set fixed number of output decimal places (e.g. 1.0 -> '1.00', 1.2345 -> 1.23, 1.999 -> '2.00')
    FloatToDecimalValidator(output_places=2)
    ```

    Valid input: `float`
    Output: `decimal.Decimal`
    """

    # Quantum used in `.quantize()` to set a fixed number of decimal places (from constructor argument output_places)
    output_quantum: Optional[Decimal] = None

    def __init__(
        self, *,
        min_value: Optional[Union[float, int]] = None,
        max_value: Optional[Union[float, int]] = None,
        output_places: Optional[int] = None,
    ):
        """
        Create a FloatToDecimalValidator with optional value range and optional number of decimal places in output value.

        Parameters 'min_value' and 'max_value' are passed to the FloatValidator, 'output_places' behaves like in DecimalValidator.

        Parameters:
            min_value: Float or integer, specifies lowest value an input float may have (default: None, no minimum value)
            max_value: Float or integer, specifies highest value an input float may have (default: None, no maximum value)
            output_places: Integer, number of decimal places the output Decimal object shall have (default: None, output equals input)
        """
        # Pass min_value/max_value to base FloatValidator which will handle the number range check
        super().__init__(min_value=min_value, max_value=max_value)

        # Set output "quantum" (the output decimal will have the same number of decimal places as this value)
        if output_places is not None:
            if output_places < 0:
                raise InvalidValidatorOptionException('Parameter "output_places" cannot be negative.')
            self.output_quantum = Decimal('0.1') ** output_places

    def validate(self, input_data: Any) -> Decimal:
        """
        Validate input data as a float, check number range, then convert it to a Decimal object.
        """
        # First, validate input data as a float (this will check that the number is finite and check against min_value/max_value)
        input_float = super().validate(input_data)

        # Convert float (to string) to Decimal
        try:
            # Cast to string first to get more sensible values (e.g. '1.234' instead of '1.233999999999999985789145284797996282...')
            decimal_out = Decimal(str(input_float))
        except InvalidOperation:  # pragma: nocover
            raise InvalidDecimalError()

        # Set fixed number of decimal places (if wanted)
        if self.output_quantum is not None:
            return decimal_out.quantize(self.output_quantum)
        else:
            return decimal_out
