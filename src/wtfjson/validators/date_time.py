# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from ..abstract_input import AbstractInput
from ..fields import Field
from ..validators import Validator
from ..exceptions import ValidationError


class DateTime(Validator):
    default_message = 'invalid datetime'

    def __init__(self, localized: bool = False, accept_utc=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.localized = localized
        self.accept_utc = accept_utc

    def __call__(self, value: str, form: AbstractInput, field: Field):
        if not self.localized:
            if self.accept_utc and value[-1] == 'Z':
                value = value[:-1]
            if '.' in value:
                value = value.split('.')[0]
            if len(value) != 19:
                raise ValidationError(self.default_message)
            try:
                field.data_processed = datetime.fromisoformat(value)
            except ValueError:
                raise ValidationError(self.message)
            return
        if len(value) < 19:
            raise ValidationError(self.default_message)
        if len(value) in [19, 20]:
            if value[-1] == 'Z':
                value = value[:-1]
            try:
                if len(value) == 19:
                    field.data_processed = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
                else:
                    field.data_processed = datetime.fromisoformat(value)
            except ValueError:
                raise ValidationError(self.message)
            return
        try:
            field.data_processed = datetime.fromisoformat(value)
        except ValueError:
            raise ValidationError(self.message)
