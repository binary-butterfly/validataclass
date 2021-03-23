# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import List, Any, Optional

from .abstract_input import AbstractInput
from .fields import UnboundField
from .validators import Validator
from .util import unset_value


class DictInput(AbstractInput):
    _fields: dict
    _validators: List[Validator]

    def __init__(self, data: Any, remove_none: bool = False):
        super().__init__()

        # first: init vars
        self._fields = {}
        self._validators = []

        # second: init fields
        for field_name in dir(self):
            if field_name in ['errors', 'has_errors', 'out', 'data']:
                continue
            if isinstance(getattr(self, field_name), UnboundField):
                unbound_field = getattr(self, field_name)
                self._fields[field_name] = unbound_field.bind(self, field_name)
                setattr(self, field_name, self._fields[field_name])

        # third: load data
        for field_name, field in self._fields.items():
            if field_name in data:
                if remove_none and data[field_name] is None:
                    continue
                field.process_in(data[field_name], remove_none)

    def validate(self) -> bool:
        for field_name, field in self._fields.items():
            if not field.validate():
                self._errors.update(field.errors)
        self._validated = True
        return not self.has_errors

    def populate_obj(self, obj, exclude: Optional[List[str]] = None):
        self._ensure_validated()
        for field_name, field in self._fields.items():
            if exclude is None or field_name not in exclude:
                if field.out is not unset_value:
                    setattr(obj, field.populate_to if field.populate_to else field_name, field.out)

    def to_dataclass(self, dataclass):
        self._ensure_validated()
        if hasattr(dataclass, 'from_dict'):
            return dataclass.from_dict(**self.out)
        return dataclass(**self.out)

    @property
    def data(self):
        self._ensure_validated()
        return {field_name: field.data for field_name, field in self._fields.items()}  # TODO: get fields back

    @property
    def out(self):
        self._ensure_validated()
        return {field_name: field.out for field_name, field in self._fields.items() if field.out is not unset_value}
