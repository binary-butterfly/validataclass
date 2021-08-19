# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from .validator import Validator
from wtfjson.exceptions import ValidationError, ListItemsValidationError


class ListValidator(Validator):
    """
    Validator for lists that validates list items with a specified item validator.
    Raises a `ListItemsValidationError` containing the validation errors of the item validator when one or more
    items failed validation.

    Example:
        ListValidator(item_validator=IntegerValidator())

    Valid input: [item1, item2, ...] (if all items are valid input for the item validator)
    Output: [validated_item1, validated_item2, ...]
    """

    # Validator used to validate the list items
    item_validator: Validator

    def __init__(self, item_validator: Validator):
        self.item_validator = item_validator

    def validate(self, input_data: Any) -> list:
        """
        Validate input data. Returns a validated list.
        """
        self._ensure_type(input_data, list)

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
