# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Union, Optional

__all__ = [
    'ValidationError',
    'RequiredValueError',
    'InvalidTypeError',
    'InternalValidationError',
]


class ValidationError(Exception):
    """
    Exception that is raised by validators if the input data is not valid. Can be subclassed for specific errors.

    Contains a string error code (usually in snake_case) to describe the error that can be used by frontends to generate human readable
    error messages. Optionally it can contain additional fields for further information, e.g. for an 'invalid_length' error there could
    be fields like 'min' and 'max' to tell the client what length an input string is supposed to have. Exceptions for combound validators
    (like `ListValidator` and `DictValidator`) could also contain nested exceptions.

    The optional 'reason' attribute can be used to further describe an error with a human readable string (e.g. if some input is only
    invalid under certain conditions and the error code alone does not make enough sense, for example a 'required_field' error on a field
    that usually is optional could have a 'reason' string like "Field is required when $someOtherField is defined."

    Use `exception.to_dict()` to get a dictionary suitable for generating JSON responses.
    """
    code: str = 'unknown_error'
    reason: Optional[str] = None
    extra_data: dict = None

    def __init__(self, *, code: str = None, reason: Optional[str] = None, **kwargs):
        if code is not None:
            self.code = code
        if reason is not None:
            self.reason = reason
        self.extra_data = kwargs

    def to_dict(self) -> dict:
        """
        Generate a dictionary containing error information, suitable as response to the user.
        May be overridden by subclasses to extend the dictionary.
        """
        extra_data = self.extra_data if self.extra_data is not None else {}
        reason = {'reason': self.reason} if self.reason is not None else {}
        return {
            'code': self.code,
            **reason,
            **extra_data,
        }


class RequiredValueError(ValidationError):
    """
    Validation error raised when None is passed as input data (unless using `Noneable`).
    """
    code = 'required_value'


class InvalidTypeError(ValidationError):
    """
    Validation error raised when the input data has the wrong data type.

    Contains either 'expected_type' (string) or 'expected_types' (list of strings) as extra fields, depending on whether there is
    a single or multiple allowed types.

    Note that this is about the raw input data, not about its content. For example, `DecimalValidator` parses a string to a Decimal
    object, so it would raise this error when the input data is anything else but a string, with 'expected_type' being set to 'str',
    not to 'Decimal' or similar. If the input is a string but not a valid decimal value, a different ValidationError will be raised.
    """
    code = 'invalid_type'
    expected_types: list[str] = None

    def __init__(self, *, expected_types: Union[type, str, list[Union[type, str]]], **kwargs):
        super().__init__(**kwargs)

        if type(expected_types) is not list:
            expected_types = [expected_types]
        self.expected_types = [t if type(t) is str else t.__name__ for t in expected_types]

    def to_dict(self):
        base_dict = super().to_dict()
        if len(self.expected_types) == 1:
            base_dict.update({'expected_type': self.expected_types[0]})
        else:
            base_dict.update({'expected_types': self.expected_types})
        return base_dict


class InternalValidationError(ValidationError):
    """
    Validation error raised when an unhandled exception (that is not a `ValidationError` subclass) occurs, e.g. in post validation.

    The unhandled exception can be wrapped inside the 'internal_error' argument, which will NOT be included in `to_dict()` but will
    be accessible for debugging purposes.
    """
    code = 'internal_error'
    internal_error: Exception = None

    def __init__(self, *, internal_error: Optional[Exception] = None, **kwargs):
        super().__init__(**kwargs)
        self.internal_error = internal_error
