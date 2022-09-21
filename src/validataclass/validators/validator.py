"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import inspect
import warnings
from abc import ABC, abstractmethod
from typing import Any, Union, List

from validataclass.exceptions import RequiredValueError, InvalidTypeError

__all__ = [
    'Validator',
]


class Validator(ABC):
    """
    Base class for building extendable validator classes that validate, sanitize and transform input.
    """

    def __init_subclass__(cls, **kwargs):
        # Check if subclasses are future-proof
        if inspect.getfullargspec(cls.validate).varkw is None:
            warnings.warn(
                "Validator classes will be required to accept arbitrary keyword arguments in their validate() method "
                f"in the future. Please add **kwargs to the list of parameters of {cls.__name__}.validate().",
                DeprecationWarning
            )

        super().__init_subclass__(**kwargs)

    @abstractmethod  # pragma: nocover
    def validate(self, input_data: Any, **kwargs):
        """
        Validates input data. Returns sanitized data or raises a `ValidationError` (or any subclass).

        This method must be implemented in validator class.

        Note: When implementing a validator class, make sure to add `**kwargs` to the method parameters. This base
        method currently does not have this parameter for compatibility reasons. However, this will change in the
        future, making it mandatory for a Validator subclass to accept arbitrary keyword arguments (which can be used
        for context-sensitive validation).
        """
        raise NotImplementedError()

    def validate_with_context(self, input_data: Any, **kwargs):
        """
        This method is a wrapper for `validate()` that always accepts arbitrary keyword arguments (which can be used
        for context-sensitive validation).

        If the `validate()` method of this class supports arbitrary keyword arguments, the keyword arguments are passed
        to the `validate()` method. Otherwise, the `validate()` method is called only with the input value and no other
        arguments.

        NOTE: This method is only needed for compatibility reasons and will become obsolete in the future, when every
        Validator class will be required to accept arbitrary keyword arguments (probably in version 1.0).

        Use this method only if you want/need to pass context arguments to a validator and don't know for sure that the
        validator accepts keyword arguments (e.g. because you don't know the class of the validator).
        """
        if inspect.getfullargspec(self.validate).varkw is not None:
            return self.validate(input_data, **kwargs)  # noqa (unexpected argument)
        else:
            return self.validate(input_data)

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
