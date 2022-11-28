"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import deepcopy
from typing import Any

from .validator import Validator

__all__ = [
    'DiscardValidator',
]


class DiscardValidator(Validator):
    """
    Special validator that discards any input and always returns a predefined value.

    This validator accepts any input of any type, but ignores it entirely and always returns the same predefined value
    instead.

    By default, the returned value is `None`. This can be changed using the `output_value` parameter.

    This validator should never raise any validation errors, since it doesn't validate anything.

    Examples:

    ```
    # Accept anything, always returns None
    DiscardValidator()

    # Accepts anything, always returns the string "discarded"
    DiscardValidator(output_value='discarded')
    ```

    See also: `RejectValidator`, `AnythingValidator`

    Valid input: Anything
    Output: `None` (or output value specified in constructor)
    """

    # Value that is returned by the validator
    output_value: Any

    def __init__(self, *, output_value: Any = None):
        """
        Create a DiscardValidator.

        Parameters:
            output_value: Value of any type that is returned for any input (default: None)
        """
        self.output_value = output_value

    def validate(self, input_data: Any, **kwargs) -> Any:
        """
        Validate input data. Discards any input and always returns None (or the specified `output_value`).
        """
        return deepcopy(self.output_value)
