"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

# Requirements for the __getattr__ definition below
import importlib
import warnings
from typing import Any

# Re-export symbols from modules
from .datetime_range import (
    BaseDateTimeRange,
    DateTimeOffsetRange,
    DateTimeRange,
)
from .unset_value import (
    OptionalUnset,
    OptionalUnsetNone,
    UnsetValue,
    UnsetValueType,
    unset_to_none,
)

__all__ = [
    'BaseDateTimeRange',
    'DateTimeOffsetRange',
    'DateTimeRange',
    'OptionalUnset',
    'OptionalUnsetNone',
    'UnsetValue',
    'UnsetValueType',
    'unset_to_none',
]


# DEPRECATED: Allow importing of moved modules for compatibility reasons. This is going to be removed in a future
# version (presumably 1.0.0).
def __getattr__(name: str) -> Any:
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
