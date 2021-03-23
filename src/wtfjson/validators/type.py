# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional, Any
from warnings import warn

from ..abstract_input import AbstractInput
from ..fields import Field
from ..validators import Validator
from ..exceptions import StopValidation


class IsType(Validator):
    default_message = 'invalid type'

    def __init__(self, data_type, message: Optional[str] = None):
        super().__init__(message)
        self.data_type = data_type

    def __call__(self, value: Any, form: AbstractInput, field: Field):
        if type(value) is not self.data_type:
            raise StopValidation(self.message)


# Deprecated alias for 'IsType' to keep compatibility. Will be removed in a future version.
def Type(*args, **kwargs):  # noqa
    warn(
        "'Type' was renamed to 'IsType' to avoid confusion with 'typing.Type'. Please use 'IsType' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return IsType(*args, **kwargs)
