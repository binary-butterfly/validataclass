"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import deepcopy
from typing import Any, overload

from typing_extensions import TypeVar

from .validator import Validator

__all__ = [
    'DiscardValidator',
]

# Type parameter for the output value of the DiscardValidator
T_DiscardOutput = TypeVar('T_DiscardOutput', default=None)


class DiscardValidator(Validator[T_DiscardOutput]):
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
    output_value: T_DiscardOutput

    @overload
    def __init__(self, *, output_value: None = None):
        ...

    @overload
    def __init__(self, *, output_value: T_DiscardOutput):
        ...

    def __init__(self, *, output_value: Any = None):
        """
        Creates a `DiscardValidator`.

        Parameters:
            `output_value`: Value of any type that is returned for any input (default: `None`)
        """
        self.output_value = output_value

    def validate(self, input_data: Any, **kwargs: Any) -> T_DiscardOutput:
        """
        Validates input data.
        Discards any input and always returns `None` (or the specified `output_value`).
        """
        return deepcopy(self.output_value)
