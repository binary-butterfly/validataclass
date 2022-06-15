"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import importlib
import warnings

from .datetime_range import BaseDateTimeRange, DateTimeRange, DateTimeOffsetRange
from .unset_value import UnsetValue, UnsetValueType, OptionalUnset, OptionalUnsetNone

# Defining __all__ is necessary here because of the definition of __getattr__() below.
__all__ = [
    'BaseDateTimeRange', 'DateTimeRange', 'DateTimeOffsetRange',
    'UnsetValue', 'UnsetValueType', 'OptionalUnset', 'OptionalUnsetNone',
]


# DEPRECATED: Allow importing of moved modules for compatibility reasons. This is going to be removed in a future
# version (presumably 1.0.0).
def __getattr__(name):
    if name in [
        'Default', 'DefaultFactory', 'DefaultUnset', 'NoDefault',
        'validataclass', 'validataclass_field', 'ValidataclassMixin',
    ]:
        warnings.warn(
            "All dataclass related modules have been moved from validataclass.helpers to validataclass.dataclasses. "
            "Importing from the old location is still possible for compatibility reasons, but will stop working in a "
            "future version. Please adjust your imports.",
            DeprecationWarning
        )
        return getattr(importlib.import_module('validataclass.dataclasses'), name)

    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")
