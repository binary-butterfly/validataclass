# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any
from abc import abstractmethod

from .abstract_input import AbstractInput
from .util import unset_value


class ListInput(AbstractInput):
    _fields: list
    _validators: list

    def __init__(self, data: Any, remove_none: bool = False):
        super().__init__()

        if self.field is unset_value:
            raise Exception('field is required')

        # first: init vars
        self._validators = []

        # second: init field
        if type(data) != list:
            self._errors['_root'] = ['invalid type']
            self._validated = True
            return
        self._fields = []
        for i in range(0, len(data)):
            field = self.field.bind(self, str(i))
            field.process_in(data[i], remove_none)
            self._fields.append(field)

    @property
    @abstractmethod  # pragma: nocover
    def field(self):
        raise NotImplementedError()

    def validate(self) -> bool:
        if self._validated:
            return not self.has_errors
        for field in self._fields:
            if not field.validate():
                self._errors.update(field.errors)
        self._validated = True
        return not self.has_errors

    @property
    def data(self):
        self._ensure_validated()
        return [field.data for field in self._fields]

    @property
    def out(self):
        self._ensure_validated()
        return [field.out for field in self._fields if field.out is not unset_value]
