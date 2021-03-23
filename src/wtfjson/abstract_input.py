# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from .exceptions import NotValidated, InvalidData


class AbstractInput(ABC):
    _errors: dict
    _validated: bool = False

    def __init__(self):
        self._errors = {}
        self._validated = False

    @abstractmethod  # pragma: nocover
    def validate(self) -> bool:
        raise NotImplementedError()

    @property
    def has_errors(self) -> bool:
        if not self._validated:
            raise NotValidated()
        return len(self._errors.keys()) > 0

    @property
    def errors(self) -> dict:
        if not self._validated:
            raise NotValidated()
        return self._errors

    def _ensure_validated(self) -> None:
        if not self._validated:
            raise NotValidated()
        if self.has_errors:
            raise InvalidData()

    @property
    @abstractmethod  # pragma: nocover
    def data(self):
        raise NotImplementedError()

    @property
    @abstractmethod  # pragma: nocover
    def out(self):
        raise NotImplementedError()
