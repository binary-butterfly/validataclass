"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from enum import Enum
from typing import Final, Literal, TypeAlias, TypeVar, final

from typing_extensions import Self, override

__all__ = [
    'UnsetValue',
    'UnsetValueType',
    'OptionalUnset',
    'OptionalUnsetNone',
    'unset_to_none',
]

T = TypeVar('T')


# Create type for UnsetValue sentinel object as a single-value enum.
#
# Using a single-value enum has the advantage that mypy will recognize it as a singleton object and correctly narrow
# down the type in conditions like `if x is not UnsetValue`.
#
# Please also note that while Python 3.15 will finally get a sentinel class (PEP 661), we won't be using that for
# UnsetValue in the foreseeable future, unless they decide to allow custom boolean evaluation (PEP 661 sentinels are
# always truthy, but UnsetValue needs to be falsy).
@final
class UnsetValueType(Enum):
    """
    Class to represent an unset value (e.g. a field in a dataclass that has no value at all because it did not exist in
    the input data).

    Similar to the built-in `None` which is of type `NoneType`, this class is used to create the unique sentinel object
    `UnsetValue`. There can only be one instance of this class. Attempting to create a new instance of `UnsetValueType`
    or to create a copy of `UnsetValue` will always result in the same instance.
    """

    # Sentinel value
    UnsetValue = 'UnsetValue'

    def __call__(self) -> Self:
        return self

    @override
    def __repr__(self) -> str:
        return 'UnsetValue'

    @override
    def __str__(self) -> str:
        return '<UnsetValue>'

    def __bool__(self) -> Literal[False]:
        return False

    # Don't define __eq__ because the default implementation is fine (identity check), and because we would then have to
    # implement __hash__ as well, otherwise UnsetValue would be considered mutable by @dataclass.


# Create actual sentinel object
UnsetValue: Final = UnsetValueType.UnsetValue

# Type alias OptionalUnset[T] for fields with DefaultUnset: Allows either the type T or UnsetValue
OptionalUnset: TypeAlias = T | UnsetValueType

# Type alias OptionalUnsetNone[T] for fields that can be None OR UnsetValue (equivalent to OptionalUnset[T | None])
OptionalUnsetNone: TypeAlias = T | UnsetValueType | None


# Small helper function for easier conversion of UnsetValue to None
def unset_to_none(value: T | UnsetValueType) -> T | None:
    """
    Converts `UnsetValue` to `None`.

    Returns `None` if the given value is `UnsetValue`, otherwise the value is returned unmodified.
    """
    return None if isinstance(value, UnsetValueType) else value
