# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import Any

from wtfjson.exceptions import RequiredValueError, InvalidTypeError


class Validator(ABC):
    """
    Base class for building extendable validator classes that validate, sanitize and transform input.
    """

    @abstractmethod  # pragma: nocover
    def validate(self, input_data: Any):
        """
        Validates any input data with the given Validator class.
        Returns sanitized data or raises a `ValidationError` (or any subclass).
        """
        raise NotImplementedError()

    @staticmethod
    def _ensure_type(input_data: Any, expected_type: type) -> None:
        """
        Raises an InvalidTypeError if type of input data is not the expected type.
        """
        # Ensure input is not None
        if input_data is None:
            raise RequiredValueError()

        # Ensure input has correct type
        if type(input_data) is not expected_type:
            raise InvalidTypeError(expected_type=expected_type)
