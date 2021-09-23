# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

__all__ = ['UnsetValue', 'UnsetValueType']


# Class to create the UnsetValue sentinel object
class UnsetValueType:
    """
    Class to represent an unset value (e.g. a field in a dataclass that has no value at all because it did not exist in the input data).

    Similar to the built-in `None` which is of type `NoneType`, this class is used to create the unique sentinel object `UnsetValue`.
    There can only be one instance of this class. Attempting to create a new instance of UnsetValueType or to create a copy of UnsetValue
    will always result in the same instance.
    """

    def __call__(self):
        return self

    def __repr__(self):
        return 'UnsetValue'

    def __str__(self):
        return '<UnsetValue>'

    def __bool__(self):
        return False


# Create sentinel object and redefine __new__ so that the object cannot be cloned
UnsetValue = UnsetValueType()
UnsetValueType.__new__ = lambda cls: UnsetValue
