# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import Any, Union, List

from wtfjson.exceptions import RequiredValueError, InvalidTypeError

__all__ = [
    'Validator',
]


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
    def _ensure_not_none(input_data: Any) -> None:
        """
        Raises a `RequiredValueError` if input data is None.
        """
        # Ensure input is not None
        if input_data is None:
            raise RequiredValueError()

    def _ensure_type(self, input_data: Any, expected_types: Union[type, List[type]]) -> None:
        """
        Checks if input data is not None and has the expected type (or one of multiple expected types).

        Raises `RequiredValueError` and `InvalidTypeError`.
        """
        # Ensure input is not None
        self._ensure_not_none(input_data)

        # Normalize expected_types to a list
        if type(expected_types) is not list:
            expected_types = [expected_types]

        # Ensure input has correct type
        if type(input_data) not in expected_types:
            raise InvalidTypeError(expected_types=expected_types)
