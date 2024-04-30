"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Dict, List, Union

from .base_exceptions import ValidationError

__all__ = [
    'RequiredValueError',
    'FieldNotAllowedError',
    'InvalidTypeError',
]


class RequiredValueError(ValidationError):
    """
    Validation error raised when None is passed as input data (unless using `Noneable`).
    """
    code = 'required_value'


class FieldNotAllowedError(ValidationError):
    """
    Validation error raised by the `RejectValidator` for any input data (except for `None` if allowed by the validator).

    In practice, this error mostly is raised when the user specifies an input value for a field in a validataclass that
    uses a `RejectValidator` (e.g. because the user is not allowed to set this field).
    """
    code = 'field_not_allowed'


class InvalidTypeError(ValidationError):
    """
    Validation error raised when the input data has the wrong data type.

    Contains either `expected_type` (string) or `expected_types` (list of strings) as extra fields, depending on whether
    there is a single or multiple allowed types.

    Note that this is about the raw input data, not about its content. For example, `DecimalValidator` parses a string
    to a `Decimal` object, so it would raise this error when the input data is anything else but a string, with
    `expected_type` being set to `str`, not to `Decimal` or similar. If the input is a string but not a valid decimal
    value, a different `ValidationError` will be raised.
    """
    code = 'invalid_type'
    expected_types: List[str]

    def __init__(self, *, expected_types: Union[type, str, List[Union[type, str]]], **kwargs: Any):
        super().__init__(**kwargs)

        if not isinstance(expected_types, list):
            expected_types = [expected_types]
        self.expected_types = [self._type_to_string(t) for t in expected_types]

    @staticmethod
    def _type_to_string(_type: Union[type, str]) -> str:
        type_str = _type if isinstance(_type, str) else _type.__name__
        if type_str == 'NoneType':
            return 'none'
        return type_str

    def add_expected_type(self, new_type: Union[type, str]) -> None:
        """
        Adds a type to `expected_types` in an existing `InvalidTypeError` exception, automatically removing duplicates.
        """
        new_type = self._type_to_string(new_type)
        if new_type not in self.expected_types:
            self.expected_types.append(new_type)

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        self.expected_types.sort()
        if len(self.expected_types) == 1:
            base_dict.update({'expected_type': self.expected_types[0]})
        else:
            base_dict.update({'expected_types': self.expected_types})
        return base_dict
