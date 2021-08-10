# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError


class DictFieldsValidationError(ValidationError):
    """
    Validation error raised by `DictValidator` when one or more dict fields has validation errors, i.e. errors raised
    by the 'field_validators' or the 'default_validator'.

    Contains the extra field 'field_errors', which is a dictionary containing further `ValidationErrors`. The keys of
    the dictionary are the names of the invalid dict fields.

    The implementation of `to_dict()` recursively converts the field validation errors to dictionaries.
    """
    code = 'field_errors'
    field_errors: dict

    def __init__(self, *, field_errors: dict[str, ValidationError]):
        assert all(isinstance(error, ValidationError) for error in field_errors.values())
        self.field_errors = field_errors

    def to_dict(self):
        return {
            'code': self.code,
            'field_errors': {
                field_name: error.to_dict() for field_name, error in self.field_errors.items()
            },
        }


class DictInvalidKeyTypeError(ValidationError):
    """
    Validation error raised by `DictValidator` when one or more keys of the input dictionary has an invalid type,
    i.e. the key is not a string.

    This error should never occur when working with JSON input data, since JSON only allows strings as keys anyway,
    so a correct JSON parser should never generate dictionaries with non-string keys.
    """
    code = 'dict_invalid_key_type'


class DictRequiredFieldError(ValidationError):
    """
    Validation error raised by `DictValidator` when a required field does not exist.

    This is different from `RequiredValueError` which will be raised if a field *does* exist but has None as value,
    *regardless* of the field being required or optional.

    To define a field that is optional (i.e. allowed to be missing in an input dictionary) *and* is allowed to exist
    with None as value, combine `required_fields` / `optional_fields` with the `Noneable` validator.
    """
    code = 'required_field'
