# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date

from ..abstract_input import AbstractInput
from ..fields import Field
from ..validators import Validator
from ..exceptions import ValidationError


class Date(Validator):
    default_message = 'invalid date'

    def __call__(self, value: str, form: AbstractInput, field: Field):
        if len(value) != 10 or value[4] != '-' or value[7] != '-':
            raise ValidationError(self.default_message)
        try:
            field.data_processed = date(int(value[0:4]), int(value[5:7]), int(value[8:10]))
        except ValueError:
            raise ValidationError(self.message)
