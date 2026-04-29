"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from .anything_validator import AnythingValidator
from .dict_validator import DictValidator

__all__ = [
    'AnyDictValidator',
]


class AnyDictValidator(DictValidator[object]):
    """
    Validator that accepts any dictionary, as long as the keys are strings (like the `DictValidator`).

    This is a subclassed `DictValidator` that uses an `AnythingValidator` as the default validator, i.e. it's used for
    every value in the dictionary. The `AnythingValidator` does no validation and accepts everything.

    Examples:

    ```
    # Validator that accepts any dictionary with string keys
    AnyDictValidator()
    ```

    Valid input: Any `dict[str, object]`
    Output: Unmodified input dictionary
    """

    def __init__(self) -> None:
        """
        Creates an `AnyDictValidator`.
        """
        # Initialize the underlying DictValidator with an AnythingValidator that validates and accepts every field.
        super().__init__(
            default_validator=AnythingValidator(),
        )
