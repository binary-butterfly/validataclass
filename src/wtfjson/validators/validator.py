# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any

from ..abstract_input import AbstractInput
from ..fields import Field


class Validator(ABC):
    default_message = 'common error'

    def __init__(self, message: Optional[str] = None):
        self.message = message if message is not None else self.default_message

    @abstractmethod  # pragma: nocover
    def __call__(self, value: Any, parent: AbstractInput, field: Field) -> None:
        pass
