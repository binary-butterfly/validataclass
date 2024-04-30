"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Optional, TypeVar, Union

from typing_extensions import Self

__all__ = [
    'UnsetValue',
    'UnsetValueType',
    'OptionalUnset',
    'OptionalUnsetNone',
    'unset_to_none',
]

T = TypeVar('T')


# Class to create the UnsetValue sentinel object
class UnsetValueType:
    """
    Class to represent an unset value (e.g. a field in a dataclass that has no value at all because it did not exist in
    the input data).

    Similar to the built-in `None` which is of type `NoneType`, this class is used to create the unique sentinel object
    `UnsetValue`. There can only be one instance of this class. Attempting to create a new instance of `UnsetValueType`
    or to create a copy of `UnsetValue` will always result in the same instance.
    """

    def __call__(self) -> Self:
        return self

    def __repr__(self) -> str:
        return 'UnsetValue'

    def __str__(self) -> str:
        return '<UnsetValue>'

    def __bool__(self) -> bool:
        return False

    # Don't define __eq__ because the default implementation is fine (identity check), and because we would then have to
    # implement __hash__ as well, otherwise UnsetValue would be considered mutable by @dataclass.


# Create sentinel object and redefine __new__ so that the object cannot be cloned
UnsetValue = UnsetValueType()
UnsetValueType.__new__ = lambda cls: UnsetValue  # type: ignore

# Type alias OptionalUnset[T] for fields with DefaultUnset: Allows either the type T or UnsetValue
OptionalUnset = Union[T, UnsetValueType]

# Type alias OptionalUnsetNone[T] for fields that can be None OR UnsetValue (equivalent to OptionalUnset[Optional[T]])
OptionalUnsetNone = OptionalUnset[Optional[T]]


# Small helper function for easier conversion of UnsetValue to None
def unset_to_none(value: OptionalUnset[T]) -> Optional[T]:
    """
    Converts `UnsetValue` to `None`.

    Returns `None` if the given value is `UnsetValue`, otherwise the value is returned unmodified.
    """
    return None if isinstance(value, UnsetValueType) else value
