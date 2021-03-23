# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union, Callable

from ..abstract_input import AbstractInput
from ..fields import Field
from ..validators import Validator
from ..exceptions import ValidationError, InvalidData


class DateTimeRange(Validator):
    default_message = 'datetime out of range'  # TODO: any beautiful idea how to put min / max in there?

    def __init__(self,
                 minus: Optional[timedelta] = None,
                 plus: Optional[timedelta] = None,
                 orientation: Optional[Union[Callable, datetime]] = None,
                 message: Optional[str] = None):
        super().__init__(message)
        if minus is None and plus is None:
            raise InvalidData()
        if minus is not None and plus is not None and minus > plus:
            raise InvalidData()
        self.minus = minus
        self.plus = plus
        self.orientation = orientation

    def __call__(self, value: Any, form: AbstractInput, field: Field):
        if type(value) is not datetime:
            return
        if self.orientation is None:
            min = (datetime.utcnow() + self.minus) if self.minus else None
            max = (datetime.utcnow() + self.plus) if self.plus else None
        elif type(self.orientation) is datetime:
            min = (self.orientation + self.minus) if self.minus else None
            max = (self.orientation + self.plus) if self.plus else None
        else:
            min = (self.orientation() + self.minus) if self.minus else None
            max = (self.orientation() + self.plus) if self.plus else None
        if min is not None and value < min:
            raise ValidationError(self.message)
        if max is not None and value > max:
            raise ValidationError(self.message)
