# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Union
from datetime import date

from ..fields import Field
from ..validators import IsType, Date
from ..util import UnsetValue


class DateField(Field):
    pre_validators = [
        IsType(data_type=str),
        Date()
    ]

    @property
    def data(self) -> Union[date, UnsetValue]:
        return super().data

    @property
    def out(self) -> Union[date, UnsetValue]:
        return super().out
