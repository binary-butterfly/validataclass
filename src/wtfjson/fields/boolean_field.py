# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from ..fields import Field
from ..validators import IsType


class BooleanField(Field):
    pre_validators = [
        IsType(data_type=bool)
    ]
