"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from collections.abc import Callable
from copy import copy, deepcopy
from typing import Any, NoReturn

from typing_extensions import Self

from validataclass.helpers import UnsetValue, UnsetValueType

__all__ = [
    'Default',
    'DefaultFactory',
    'DefaultUnset',
    'NoDefault',
]


# Helper objects for setting default values for validator fields

class Default:
    """
    (Base) class for specifying default values for dataclass validator fields.
    Values are deepcopied on initialization and on retrieval.

    Examples: `Default(None)`, `Default(42)`, `Default('empty')`, `Default([])`

    See also: `DefaultFactory()`, `DefaultUnset`, `NoDefault`
    """
    value: Any = None

    def __init__(self, value: Any = None):
        self.value = deepcopy(value)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'

    def __eq__(self, other: Any) -> bool:
        if isinstance(self, type(other)):
            return bool(self.value == other.value)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)

    def get_value(self) -> Any:
        return deepcopy(self.value)

    def needs_factory(self) -> bool:
        """
        Returns True if a dataclass default_factory is needed for this Default object, for example if the value is a
        mutable object (e.g. a list) that needs to be copied.
        """
        # If copying the value results in the identical object, no factory is needed (a shallow copy is sufficient to
        # test this)
        return copy(self.value) is not self.value


class DefaultFactory(Default):
    """
    Class for specifying factories (functions or classes) to dynamically generate default values.

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
    factory: Callable[[], Any]

    def __init__(self, factory: Callable[[], Any]):
        super().__init__()
        self.factory = factory

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.factory!r})'

    def __eq__(self, other: Any) -> bool:
        if isinstance(self, type(other)):
            return isinstance(other, DefaultFactory) and bool(self.factory == other.factory)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.factory)

    def get_value(self) -> Any:
        return self.factory()

    def needs_factory(self) -> bool:
        return True


# Temporary class to create the DefaultUnset sentinel, class will be deleted afterwards
class _DefaultUnset(Default):
    """
    Class for creating the sentinel object `DefaultUnset`, which is a shortcut for `Default(UnsetValue)`.
    """

    def __init__(self) -> None:
        super().__init__(UnsetValue)

    def __repr__(self) -> str:
        return 'DefaultUnset'

    def get_value(self) -> UnsetValueType:
        return UnsetValue

    def needs_factory(self) -> bool:
        return False

    # For convenience: Allow DefaultUnset to be used as `DefaultUnset()`, returning the sentinel itself.
    def __call__(self) -> Self:
        return self


# Create sentinel object DefaultUnset, redefine __new__ to always return the same instance, and delete temporary class
DefaultUnset = _DefaultUnset()
_DefaultUnset.__new__ = lambda cls: DefaultUnset  # type: ignore
del _DefaultUnset


# Temporary class to create the NoDefault sentinel, class will be deleted afterwards
class _NoDefault(Default):
    """
    Class for creating the sentinel object `NoDefault` which specifies that a field has no default value, i.e. the field
    is required.

    A validataclass field with `NoDefault` is equivalent to a validataclass field without specified default.
    """

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return 'NoDefault'

    def __eq__(self, other: Any) -> bool:
        # Nothing is equal to NoDefault except itself
        return type(self) is type(other)

    def __hash__(self) -> int:
        # Use default implementation
        return object.__hash__(self)

    def get_value(self) -> NoReturn:
        raise ValueError('No default value specified!')

    # For convenience: Allow NoDefault to be used as `NoDefault()`, returning the sentinel itself.
    def __call__(self) -> Self:
        return self


# Create sentinel object NoDefault, redefine __new__ to always return the same instance, and delete temporary class
NoDefault = _NoDefault()
_NoDefault.__new__ = lambda cls: NoDefault  # type: ignore
del _NoDefault
