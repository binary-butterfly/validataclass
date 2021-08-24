# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from .validator import Validator
from wtfjson.exceptions import ValidationError, ListItemsValidationError, ListLengthError, InvalidValidatorOptionException

__all__ = [
    'ListValidator',
]


class ListValidator(Validator):
    """
    Validator for lists that validates list items with a specified item validator.

    Raises a `ListItemsValidationError` containing the validation errors of the item validator when one or more
    items failed validation.

    Optionally a minimum and/or maximum length for the list can be specified.

    Example:

    ```
    # Validator for lists of integers (equivalent forms, use whichever you prefer)
    ListValidator(IntegerValidator())
    ListValidator(item_validator=IntegerValidator())

    # Do not allow empty lists
    ListValidator(IntegerValidator(), min_length=1)

    # Do not allow empty lists or lists with more than 20 items
    ListValidator(IntegerValidator(), min_length=1, max_length=20)
    ```

    Valid input: [item1, item2, ...] (if all items are valid input for the item validator)
    Output: [validated_item1, validated_item2, ...]
    """

    # Validator used to validate the list items
    item_validator: Validator

    # List length constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    def __init__(self, item_validator: Validator, *, min_length: Optional[int] = None, max_length: Optional[int] = None):
        """
        Create a ListValidator with a given item validator and optional minimum/maximum list length requirements.

        Parameters:
            item_validator: Validator, used to validate the items in the list (required)
            min_length: Integer, specifies minimum length of input list (default: None, no minimum length)
            max_length: Integer, specifies maximum length of input list (default: None, no maximum length)
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

    def validate(self, input_data: Any) -> list:
        """
        Validate input data. Returns a validated list.
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
                validated_list.append(self.item_validator.validate(item))
            except ValidationError as error:
                validation_errors[index] = error

        # Raise validation error if any item failed to be validated
        if validation_errors:
            raise ListItemsValidationError(item_errors=validation_errors)

        # Return list of validated items
        return validated_list
