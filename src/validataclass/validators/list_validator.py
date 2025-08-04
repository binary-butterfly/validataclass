"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Generic, TypeVar

from validataclass.exceptions import (
    InvalidValidatorOptionException,
    ListItemsValidationError,
    ListLengthError,
    ValidationError,
)
from .validator import Validator

__all__ = [
    'ListValidator',
    'T_ListItem',
]

# Type parameter for the list items in the output of a ListValidator
T_ListItem = TypeVar('T_ListItem')


class ListValidator(Validator[list[T_ListItem]], Generic[T_ListItem]):
    """
    Validator for lists that validates list items with a specified item validator.

    Raises a `ListItemsValidationError` containing the validation errors of the item validator when one or more
    items failed validation.

    Optionally a minimum and/or maximum length for the list can be specified.

    If the parameter `discard_invalid` is set, the validator will NOT raise validation errors if the item validator
    fails, but silently discard the invalid items. The result will be a list with only the valid items (which can be an
    empty list if all items are invalid). If `minimum_length` is set, the length of the list will be checked a second
    time after discarding invalid items to make sure that the resulting list still fulfills the minimum length
    requirement.

    Example:

    ```
    # Validator for lists of integers (equivalent forms, use whichever you prefer)
    ListValidator(IntegerValidator())
    ListValidator(item_validator=IntegerValidator())

    # Do not allow empty lists
    ListValidator(IntegerValidator(), min_length=1)

    # Do not allow empty lists or lists with more than 20 items
    ListValidator(IntegerValidator(), min_length=1, max_length=20)

    # Discard items that are not a valid integers instead of raising an error
    # Example: [3, 'banana', 42, None] -> [3, 42]
    ListValidator(IntegerValidator(), discard_invalid=True)

    # Discard invalid items, but with a minimum list length
    # Examples:
    # [3, 'banana', 42] -> [3]
    # [3]               -> ListLengthError (raised BEFORE validating the items)
    # [3, 'foo', 'bar'] -> ListLengthError (raised AFTER validating the items, the resulting list would be too short)
    ListValidator(IntegerValidator(), min_length=2, discard_invalid=True)
    ```

    Valid input: `[item1, item2, ...]` (if all items are valid input for the item validator)
    Output: `[validated_item1, validated_item2, ...]`
    """

    # Validator used to validate the list items
    item_validator: Validator[T_ListItem]

    # List length constraints
    min_length: int | None = None
    max_length: int | None = None

    # Discard invalid items instead of raising error
    discard_invalid: bool = False

    def __init__(
        self,
        item_validator: Validator[T_ListItem],
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        discard_invalid: bool = False
    ):
        """
        Creates a `ListValidator` with a given item validator and optional minimum/maximum list length requirements.

        Parameters:
            `item_validator`: Validator used to validate the items in the list (required)
            `min_length`: Integer, specifies minimum length of input list (default: `None`, no minimum length)
            `max_length`: Integer, specifies maximum length of input list (default: `None`, no maximum length)
            `discard_invalid`: Boolean, if `True`, will silently discard invalid items instead of raising error
        """
        # Set validator used on each list item
        self.item_validator = item_validator

        # Check parameter validity
        if min_length is not None and min_length < 0:
            raise InvalidValidatorOptionException('Parameter "min_length" cannot be negative.')
        if max_length is not None and max_length < 0:
            raise InvalidValidatorOptionException('Parameter "max_length" cannot be negative.')
        if min_length is not None and max_length is not None and min_length > max_length:
            raise InvalidValidatorOptionException('Parameter "min_length" cannot be greater than "max_length".')

        self.min_length = min_length
        self.max_length = max_length
        self.discard_invalid = discard_invalid

    def validate(self, input_data: Any, **kwargs: Any) -> list[T_ListItem]:
        """
        Validates input data. Returns a validated list.
        """
        self._ensure_type(input_data, list)

        # Check number of items before validating them
        if self.min_length is not None and len(input_data) < self.min_length:
            raise ListLengthError(min_length=self.min_length, max_length=self.max_length)
        if self.max_length is not None and len(input_data) > self.max_length:
            raise ListLengthError(min_length=self.min_length, max_length=self.max_length)

        validated_list = []
        validation_errors = {}

        # Apply item_validator to all list items and collect validation errors
        for index, item in enumerate(input_data):
            try:
                validated_list.append(self.item_validator.validate_with_context(item, **kwargs))
            except ValidationError as error:
                validation_errors[index] = error

        # Check one more time if the validated list is not too short
        if self.discard_invalid:
            if self.min_length is not None and len(validated_list) < self.min_length:
                raise ListLengthError(min_length=self.min_length, max_length=self.max_length)

        # Raise validation error if discard_invalid is False,
        # and if any item failed to be validated
        elif validation_errors:
            raise ListItemsValidationError(item_errors=validation_errors)

        # Return list of validated items
        return validated_list
