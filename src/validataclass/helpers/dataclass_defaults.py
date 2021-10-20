"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import deepcopy
from typing import Any, NoReturn, Callable

from .unset_value import UnsetValue, UnsetValueType

# Specify which functions/symbols are imported with `from module import *`
__all__ = [
    'Default',
    'DefaultFactory',
    'DefaultUnset',
    'NoDefault',
]


# Helper objects for setting default values for validator fields

class Default:
    """
    (Base) class for specifying default values for dataclass validator fields. Values are deepcopied on initialization and on retrieval.

    Examples: `Default(None)`, `Default(42)`, `Default('empty')`, `Default([])`

    See also: `DefaultFactory()`, `DefaultUnset`, `NoDefault`
    """
    value: Any = None

    def __init__(self, value: Any = None):
        self.value = deepcopy(value)

    def __repr__(self):
        return f'{type(self).__name__}({self.value!r})'

    def get_value(self) -> Any:
        return deepcopy(self.value)


class DefaultFactory(Default):
    """
    Class for specifying factories (functions or classes) to dynamically generate default values.

    Examples:
        `DefaultFactory(list)` (generates an empty list)
        `DefaultFactory(SomeClass)` (generates new instances of `SomeClass`)
        `DefaultFactory(lambda: some_expression)` (uses a lambda to evaluate an expression to generate default values)
    """
    factory: Callable

    def __init__(self, factory: Callable):
        super().__init__()
        self.factory = factory

    def __repr__(self):
        return f'{type(self).__name__}({self.factory!r})'

    def get_value(self) -> Any:
        return self.factory()


# Temporary class to create the DefaultUnset sentinel, class will be deleted afterwards
class _DefaultUnset(Default):
    """
    Class for creating the sentinel object `DefaultUnset`, which is a shortcut for `Default(UnsetValue)`.
    """

    def __init__(self):
        super().__init__(UnsetValue)

    def __repr__(self):
        return 'DefaultUnset'

    def get_value(self) -> UnsetValueType:
        return UnsetValue

    # For convenience: Allow DefaultUnset to be used as `DefaultUnset()`, returning the sentinel itself.
    def __call__(self):
        return self


# Create sentinel object DefaultUnset, redefine __new__ to always return the same instance, and delete temporary class
DefaultUnset = _DefaultUnset()
_DefaultUnset.__new__ = lambda cls: DefaultUnset
del _DefaultUnset


# Temporary class to create the NoDefault sentinel, class will be deleted afterwards
class _NoDefault(Default):
    """
    Class for creating the sentinel object `NoDefault` which specifies that a field has no default value (meaning it is required).
    """

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return 'NoDefault'

    def get_value(self) -> NoReturn:
        raise ValueError('No default value specified!')

    # For convenience: Allow NoDefault to be used as `NoDefault()`, returning the sentinel itself.
    def __call__(self):
        return self


# Create sentinel object NoDefault, redefine __new__ to always return the same instance, and delete temporary class
NoDefault = _NoDefault()
_NoDefault.__new__ = lambda cls: NoDefault
del _NoDefault
