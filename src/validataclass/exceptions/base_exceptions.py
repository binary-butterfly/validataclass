"""
validataclass
Copyright (c) 2024, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Dict, Optional

__all__ = [
    'ValidationError',
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
    extra_data: Optional[dict] = None

    def __init__(self, *, code: Optional[str] = None, reason: Optional[str] = None, **kwargs):
        if code is not None:
            self.code = code
        if reason is not None:
            self.reason = reason
        self.extra_data = {key: value for key, value in kwargs.items() if value is not None}

    def __repr__(self):
        params_string = ', '.join(f'{key}={value}' for key, value in self._get_repr_dict().items() if value is not None)
        return f'{type(self).__name__}({params_string})'

    def __str__(self):
        return self.__repr__()

    def _get_repr_dict(self) -> Dict[str, str]:
        """
        Returns a dictionary representing the error fields as strings (e.g. by applying `repr()` on the values).
        Used by `__repr__` to generate a string representation of the form "ExampleValidationError(code='foo', reason='foo', ...)".
        The default implementation calls `to_dict()` and applies `repr()` on all values.
        """
        return {
            key: repr(value) for key, value in self.to_dict().items() if value is not None
        }

    def to_dict(self) -> dict:
        """
        Generate a dictionary containing error information, suitable as response to the user.
        May be overridden by subclasses to extend the dictionary.
        """
        reason = {'reason': self.reason} if self.reason is not None else {}
        extra_data = self.extra_data if self.extra_data is not None else {}
        return {
            'code': self.code,
            **reason,
            **extra_data,
        }
