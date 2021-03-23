# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Union

from ..fields import Field
from ..validators import IsType
from ..util import UnsetValue


class FloatField(Field):
    pre_validators = [
        IsType(data_type=float)
    ]

    @property
    def data(self) -> Union[float, UnsetValue]:
        return super().data

    @property
    def out(self) -> Union[float, UnsetValue]:
        return super().out
