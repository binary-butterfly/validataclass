"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from validataclass.helpers import UnsetValue
from .noneable import Noneable
from .validator import Validator

__all__ = [
    'NoneToUnsetValue',
]


class NoneToUnsetValue(Noneable):
    """
    Shortcut variation of the `Noneable` wrapper, using `UnsetValue` as the default value.

    This is a special validator that wraps another validator, but allows `None` as the input value. If the input is
    `None`, the validator returns the special value `UnsetValue`. Otherwise the wrapped validator is used to validate
    the input.

    This validator is equivalent to `Noneable(validator, default=UnsetValue)`.

    Examples:

    ```
    # Accepts strings and None. Instead of None, UnsetValue is returned (e.g. "foo" -> "foo", None -> UnsetValue)
    NoneToUnsetValue(StringValidator())

    # Equivalent to the following:
    Noneable(StringValidator(), default=UnsetValue)
    ```

    Valid input: `None` or any data accepted by the wrapped validator
    Output: `UnsetValue` or the output of the wrapped validator
    """

    def __init__(self, validator: Validator):
        """
        Create a NoneToUnsetValue wrapper for a specified validator.
        """
        # Initialize base Noneable wrapper
        super().__init__(validator, default=UnsetValue)
