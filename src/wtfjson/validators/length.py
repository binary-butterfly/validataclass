# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from ..abstract_input import AbstractInput
from ..fields import Field
from ..validators import Validator
from ..exceptions import ValidationError, InvalidData


class Length(Validator):
    default_message = 'invalid length'  # TODO: any beautiful idea how to put min / max in there?

    def __init__(self, min: Optional[int] = None, max: Optional[int] = None, message: Optional[str] = None):
        super().__init__(message)
        if min is None and max is None:
            raise InvalidData()
        if min is not None and max is not None and min > max:
            raise InvalidData()
        self.min = min
        self.max = max

    def __call__(self, value: Any, form: AbstractInput, field: Field):
        if self.min is not None and len(value) < self.min:
            raise ValidationError(self.message)
        if self.max is not None and len(value) > self.max:
            raise ValidationError(self.message)
