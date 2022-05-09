"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Optional

from .integer_validator import IntegerValidator

__all__ = [
    'BigIntegerValidator',
]


class BigIntegerValidator(IntegerValidator):
    """
    Validator for big integer values.

    This validator is a variation of the IntegerValidator. It's exactly the same validator, just with other default
    parameters.

    While the IntegerValidator sets defaults for `min_value` and `max_value` to limit input to 32-bit integers, the
    BigIntegerValidator resets these parameters to `None` to allow arbitrarily big integers. You can still override
    these parameters, e.g. by setting `min_value=1` to allow only positive numbers.

    So basically, `BigIntegerValidator()` is identical to `IntegerValidator(min_value=None, max_value=None)`.

    Like the IntegerValidator, it also supports the parameter `allow_strings` to allow strings as input.

    Examples:

    ```
    # Accepts *any* integer (e.g. -1000000000000000, 123, 1000000000000000, but not a string like "123")
    BigIntegerValidator()

    # Accepts only positive integers (e.g. 123, 1000000000000000, but not 0 or -1)
    BigIntegerValidator(min_value=1)

    # Accepts only values in the specified range. There is no point in using the BigIntegerValidator in this case, as
    # it's identical to an IntegerValidator with the same parameters, so you should use that one instead.
    BigIntegerValidator(min_value=-100, max_value=100)

    # Accepts any integer either as a direct integer or a numeric string (e.g. "1000000000000000" -> 1000000000000000)
    BigIntegerValidator(allow_strings=True)
    ```

    Valid input: `int` (also `str` if `allow_strings=True`)
    Output: `int`
    """

    def __init__(self, *, min_value: Optional[int] = None, max_value: Optional[int] = None, allow_strings: bool = False):
        """
        Create a BigIntegerValidator.

        Parameters:
            min_value: Integer or None, smallest allowed integer value (default: None, no limit)
            max_value: Integer or None, biggest allowed integer value (default: None, no limit)
            allow_strings: Boolean, if True, numeric strings (e.g. "123") are accepted and converted to integers (default: False)
        """
        super().__init__(min_value=min_value, max_value=max_value, allow_strings=allow_strings)
