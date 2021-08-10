# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Union


class ValidationError(Exception):
    """
    Exception that is raised by validators if the input data is not valid. Can be subclassed for specific errors.

    Contains a string error code (usually in snake_case) to describe the error that can be used by frontends to
    generate human readable error messages. Optionally it can contain additional fields for further information,
    e.g. for an 'invalid_length' error there could be fields like 'min' and 'max' to tell the client what length
    an input string is supposed to have. Exceptions for combound validators (like `ListValidator` and `DictValidator`)
    could also contain nested exceptions.

    Use `exception.to_dict()` to get a dictionary suitable for generating JSON responses.
    """
    code: str = 'unknown_error'
    extra_data: dict = None

    def __init__(self, *, code: str = None, **kwargs):
        if code is not None:
            self.code = code
        self.extra_data = kwargs

    def to_dict(self):
        extra_data = self.extra_data if self.extra_data is not None else {}
        return {
            'code': self.code,
            **extra_data,
        }


class RequiredValueError(ValidationError):
    """
    Validation error raised when None is passed as input data (unless using `Noneable`).
    """
    code = 'required_value'


class InvalidTypeError(ValidationError):
    """
    Validation error raised when the input data has the wrong data type. Contains 'expected_type' as extra data.

    Note that this is about the raw input data, not about its content. For example, `DecimalValidator` parses a string
    to a Decimal object, so it would raise this error when the input data is anything else but a string, with
    'expected_type' being set to 'str', not to 'Decimal' or similar. If the input is a string but not a valid decimal
    value, a different validator error will be raised.
    """
    code = 'invalid_type'

    def __init__(self, *, expected_type: Union[type, str]):
        self.extra_data = {
            'expected_type': expected_type if isinstance(expected_type, str) else expected_type.__name__,
        }
