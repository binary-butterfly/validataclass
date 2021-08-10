# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError


class ListItemsValidationError(ValidationError):
    """
    Validation error raised by `ListValidator` when one or more list items has validation errors, i.e. errors raised
    by the 'item_validator'.

    Contains the extra field 'item_errors', which is a dictionary containing further `ValidationErrors`. The keys of
    the dictionary are the indices of the invalid list items (as given in the input list).

    The implementation of `to_dict()` recursively converts the item validation errors to dictionaries.
    """
    code = 'list_item_errors'
    item_errors: dict

    def __init__(self, *, item_errors: dict[int, ValidationError]):
        assert all(isinstance(error, ValidationError) for error in item_errors.values())
        self.item_errors = item_errors

    def to_dict(self):
        return {
            'code': self.code,
            'item_errors': {
                index: error.to_dict() for index, error in self.item_errors.items()
            },
        }
