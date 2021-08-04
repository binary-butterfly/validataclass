# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Union


class ValidationError(Exception):
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
    code = 'required_value'


class InvalidTypeError(ValidationError):
    code = 'invalid_type'

    def __init__(self, *, expected_type: Union[type, str]):
        self.extra_data = {
            'expected_type': expected_type if isinstance(expected_type, str) else expected_type.__name__,
        }
