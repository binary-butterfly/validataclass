"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal
from typing import Optional, Union

from .float_to_decimal_validator import FloatToDecimalValidator

__all__ = [
    'NumericValidator',
]


class NumericValidator(FloatToDecimalValidator):
    """
    Validator that accepts numeric values in different types (integers, floats and decimal strings) and converts them
    to `decimal.Decimal` objects.

    This validator is based on the `FloatToDecimalValidator`. In fact, the validator is basically just a shortcut for
    `FloatToDecimalValidator(allow_integers=True, allow_strings=True)`.

    The validator supports the optional parameters 'min_value', 'max_value' and 'output_places' which will be passed
    to the `FloatToDecimalValidator`.

    NOTE: Due to the way that floats work, the resulting decimals for float input values can have inaccuracies! It is
    recommended to use `DecimalValidator` with decimal strings as input data instead of using float input (e.g. strings
    like `"1.234"` instead of floats like `1.234`). This validator mainly exists for cases where you need to accept
    floats as input (e.g. with APIs that you have no control over).

    Examples:

    ```
    # Allows any numeric value (integer, float or string) and returns them as Decimals:
    # int: 123 -> Decimal('123')
    # float: -1.23 -> Decimal('-1.23')  (beware of potential float inaccuracies though)
    # str: "0.123" -> Decimal('0.123')
    NumericValidator()

    # Only allow zero or positive numbers (e.g. 0, 1000, 0.01, "0.123")
    NumericValidator(min_value=0)

    # Only allow values from -0.5 to 0.5
    NumericValidator(min_value='-0.5', max_value='0.5')

    # No input restrictions, but output Decimals always have a fixed number of decimal places:
    # 1234 -> Decimal('1234.00')
    # -0.1 -> Decimal('-0.10')
    # "0.6666" -> Decimal('0.67') (exact value depends on decimal context)
    NumericValidator(output_places=2)
    ```

    Valid input: `int`, `float`, `str` (decimal strings)
    Output: `decimal.Decimal`
    """

    def __init__(
        self, *,
        min_value: Optional[Union[Decimal, str, float, int]] = None,
        max_value: Optional[Union[Decimal, str, float, int]] = None,
        output_places: Optional[int] = None,
    ):
        """
        Create a `NumericValidator` with optional value range and optional number of decimal places in output value.

        The parameters 'min_value', 'max_value' and 'output_places' are passed to the underlying `FloatToDecimalValidator`.

        Parameters:
            min_value: Decimal, str, float or int, specifies lowest value an input float may have (default: None, no minimum value)
            max_value: Decimal, str, float or int, specifies highest value an input float may have (default: None, no maximum value)
            output_places: Integer, number of decimal places the output Decimal object shall have (default: None, output equals input)
        """
        # Initialize base FloatToDecimalValidator with allow_integers and allow_strings always being enabled
        super().__init__(
            min_value=min_value,
            max_value=max_value,
            output_places=output_places,
            allow_integers=True,
            allow_strings=True,
        )
