# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum
from typing import Union

from ..fields import Field
from ..validators import IsType, EnumValidator
from ..util import UnsetValue


class EnumField(Field):

    def __init__(self, enum, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum = enum
        self.default_validators = [
            IsType(data_type=str),
            EnumValidator(enum=enum)
        ]

    @property
    def data(self) -> Union[Enum, UnsetValue]:
        return super().data

    @property
    def out(self) -> Union[Enum, UnsetValue]:
        return super().out
