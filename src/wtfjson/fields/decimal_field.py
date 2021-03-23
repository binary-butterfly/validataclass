# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Union
from decimal import Decimal

from ..fields import Field
from ..validators import IsType, DecimalValidator
from ..util import UnsetValue


class DecimalField(Field):
    pre_validators = [
        IsType(data_type=str),
        DecimalValidator()
    ]

    @property
    def data(self) -> Union[Decimal, UnsetValue]:
        return super().data

    @property
    def out(self) -> Union[Decimal, UnsetValue]:
        return super().out
