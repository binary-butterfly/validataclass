# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from typing import Any, NoReturn

# Specify which functions/symbols are imported with `from module import *`
__all__ = [
    'Default',
    'NoDefault',
]


# Helper objects for setting default values for validator fields

class Default:
    """
    (Base) class for specifying default values for dataclass validator fields. Values are deepcopied on initialization.

    Examples: Default(None), Default(42), Default('empty'), Default([])

    See also: `DefaultFactory()`, `DefaultUnset()`, `NoDefault`
    """
    value: Any

    def __init__(self, value: Any):
        self.value = deepcopy(value)

    def __repr__(self):
        cls_name = type(self).__name__
        value = repr(self.value)
        return f'{cls_name}({value})'

    def get_value(self) -> Any:
        return self.value


# Temporary class to create the NoDefault sentinel, class will be deleted afterwards
class _NoDefault(Default):
    """
    Class for creating the sentinel object `NoDefault` which specifies that a field has no default value (meaning it is required).
    """

    def __init__(self):
        super().__init__(None)

    def __repr__(self):
        return 'NoDefault'

    def get_value(self) -> NoReturn:
        raise ValueError('No default value specified!')

    # For convenience: Allow NoDefault to be used as `NoDefault()`, returning the sentinel itself.
    def __call__(self):
        return self


# Create sentinel object, redefine __new__ so that there can always be only one NoDefault object, and delete temporary class
NoDefault = _NoDefault()
_NoDefault.__new__ = lambda cls: NoDefault
del _NoDefault
