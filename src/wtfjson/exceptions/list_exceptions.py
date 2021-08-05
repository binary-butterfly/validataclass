# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError


class ListItemsValidationError(ValidationError):
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
