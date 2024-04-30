"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Dict, Optional

from .base_exceptions import ValidationError

__all__ = [
    'ListItemsValidationError',
    'ListLengthError',
]


class ListItemsValidationError(ValidationError):
    """
    Validation error raised by `ListValidator` when one or more list items has validation errors, i.e. errors raised
    by the `item_validator`.

    Contains the extra field `item_errors`, which is a dictionary containing further `ValidationErrors`. The keys of
    the dictionary are the indices of the invalid list items (as given in the input list).

    The implementation of `to_dict()` recursively converts the item validation errors to dictionaries.
    """
    code = 'list_item_errors'
    item_errors: Dict[int, ValidationError]

    def __init__(self, *, item_errors: Dict[int, ValidationError], **kwargs: Any):
        super().__init__(**kwargs)
        assert all(isinstance(error, ValidationError) for error in item_errors.values())
        self.item_errors = item_errors

    def _get_repr_dict(self) -> Dict[str, str]:
        base_dict = super()._get_repr_dict()
        return {
            **base_dict,
            'item_errors': repr(self.item_errors),
        }

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        return {
            **base_dict,
            'item_errors': {
                index: error.to_dict() for index, error in self.item_errors.items()
            },
        }


class ListLengthError(ValidationError):
    """
    Validation error raised by `ListValidator` when a minimum and/or maximum list length is specified and the input list
    has too many or not enough items.

    May contain the extra fields `min_length` and `max_length`, depending on which are specified in the validator.
    """
    code = 'list_invalid_length'

    def __init__(self, *, min_length: Optional[int] = None, max_length: Optional[int] = None, **kwargs: Any):
        if min_length is not None:
            kwargs.update(min_length=min_length)
        if max_length is not None:
            kwargs.update(max_length=max_length)
        super().__init__(**kwargs)
