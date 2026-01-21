"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy
from typing import Any, Generic, TypeVar

from typing_extensions import Never, Self, override

from validataclass.helpers import UnsetValue, UnsetValueType

__all__ = [
    'BaseDefault',
    'Default',
    'DefaultFactory',
    'DefaultUnset',
    'NoDefault',
]

# Helper objects for setting default values for validator fields

# Type parameter for the value of a default object
T_Default = TypeVar('T_Default')


class BaseDefault(Generic[T_Default], ABC):
    """
    Base class for defining default values for dataclass validator fields.

    See also: `Default`, `DefaultFactory()`, `DefaultUnset`, `NoDefault`
    """

    @override
    def __repr__(self) -> str:
        return type(self).__name__

    @override
    def __eq__(self, other: Any) -> bool:
        return NotImplemented

    __hash__ = object.__hash__

    @abstractmethod
    def get_value(self) -> T_Default:
        """
        Get actual default value.
        """
        raise NotImplementedError

    @abstractmethod
    def needs_factory(self) -> bool:
        """
        Return True if a dataclass `default_factory` is needed for this default object, for example if the value is a
        mutable object (e.g. a list) that needs to be copied.
        """
        raise NotImplementedError


class Default(BaseDefault[T_Default]):
    """
    Class for specifying default values for dataclass validator fields.
    Values are deepcopied on initialization and on retrieval.

    Examples: `Default(None)`, `Default(42)`, `Default('empty')`, `Default([])`

    See also: `DefaultFactory()`, `DefaultUnset`, `NoDefault`
    """

    _value: T_Default
    _needs_factory: bool

    def __init__(self, value: T_Default):
        # Deepcopy the value to avoid reusing mutable objects
        self._value = deepcopy(value)

        # If copying the value resulted in the identical object, no factory is needed
        self._needs_factory = self._value is not value

    @override
    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._value!r})'

    @override
    def __eq__(self, other: Any) -> bool:
        # Only handle this if self is of the same type as other OR self is a subclass of other.
        # In other words, don't handle this if other is a completely different type or more specialized than self.
        if isinstance(self, type(other)):
            # A Default object is only equal to another Default object and only if their values are equal
            return isinstance(other, Default) and bool(self._value == other._value)
        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(self._value)

    # Deprecated: Allow DefaultUnset to be used as `DefaultUnset()`, returning the object itself.
    # TODO: Remove this in a future version.
    def __call__(self) -> Self:
        # Only allow calling if it's Default(UnsetValue) / DefaultUnset. Don't introduce new deprecated features.
        if self._value is UnsetValue:
            warnings.warn(
                "Calling default objects is deprecated. Please use `DefaultUnset` instead of `DefaultUnset()`.",
                DeprecationWarning
            )
            return self
        raise TypeError(f"'{type(self).__name__}' object is not callable")

    @override
    def get_value(self) -> T_Default:
        """
        Get actual default value.
        """
        return deepcopy(self._value)

    @override
    def needs_factory(self) -> bool:
        """
        Return True if a dataclass `default_factory` is needed for this default object, for example if the value is a
        mutable object (e.g. a list) that needs to be copied.
        """
        return self._needs_factory


class DefaultFactory(BaseDefault[T_Default]):
    """
    Class for specifying factories (functions or classes) to dynamically generate default values.

    The factory must be a callable without arguments.

    Examples:

    ```
    # Generates an empty list (i.e. list())
    DefaultFactory(list)

    # Generates new instances of SomeClass (i.e. SomeClass())
    DefaultFactory(SomeClass)

    # Uses a lambda to evaluate an expression to generate default values (here: a Date object with the current day)
    DefaultFactory(lambda: date.today())
    ```
    """

    _factory: Callable[[], T_Default]

    def __init__(self, factory: Callable[[], T_Default]):
        self._factory = factory

    @override
    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._factory!r})'

    @override
    def __eq__(self, other: Any) -> bool:
        # Only handle this if self is of the same type as other OR self is a subclass of other.
        # In other words, don't handle this if other is a completely different type or more specialized than self.
        if isinstance(self, type(other)):
            # A DefaultFactory object is only equal to another DefaultFactory object with the same factory function
            return isinstance(other, DefaultFactory) and bool(self._factory == other._factory)
        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(self._factory)

    @override
    def get_value(self) -> T_Default:
        """
        Get an actual default value by calling the factory function.
        """
        return self._factory()

    @override
    def needs_factory(self) -> bool:
        """
        Return True if a dataclass `default_factory` is needed for this default object.
        Always true for `DefaultFactory`.
        """
        return True


# Define common shortcut/alias for Default(UnsetValue)
DefaultUnset: Default[UnsetValueType] = Default(UnsetValue)


# Temporary class to create the NoDefault sentinel, class will be deleted afterwards
class _NoDefault(BaseDefault[Never]):
    """
    Class for creating the sentinel object `NoDefault` which specifies that a field has no default value, i.e. the field
    is required.

    A validataclass field with `NoDefault` is equivalent to a validataclass field without specified default.
    """

    @override
    def __repr__(self) -> str:
        return 'NoDefault'

    @override
    def __eq__(self, other: Any) -> bool:
        # Nothing is equal to NoDefault except itself
        return self is other

    __hash__ = BaseDefault.__hash__

    @override
    def get_value(self) -> Never:
        raise ValueError('No default value specified!')

    @override
    def needs_factory(self) -> bool:
        raise NotImplementedError('NoDefault can be used neither as a value nor as a factory.')

    # Deprecated: Allow NoDefault to be used as `NoDefault()`, returning the object itself.
    # TODO: Remove this in a future version.
    def __call__(self) -> Self:
        warnings.warn(
            "Calling default objects is deprecated. Please use `NoDefault` instead of `NoDefault()`.",
            DeprecationWarning
        )
        return self


# Create sentinel object NoDefault, redefine __new__ to always return the same instance, and delete temporary class
NoDefault = _NoDefault()
_NoDefault.__new__ = lambda cls: NoDefault  # type: ignore[assignment, method-assign, return-value]
del _NoDefault
