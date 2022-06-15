"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import warnings

from validataclass.dataclasses.validataclass_mixin import ValidataclassMixin

__all__ = [
    'ValidataclassMixin',
]

# DEPRECATED: This module exists only for compatibility reasons and is going to be removed in a future version (presumably 1.0.0).
warnings.warn(
    "All dataclass related modules have been moved from validataclass.helpers to validataclass.dataclasses. "
    "Importing from the old location is still possible for compatibility reasons, but will stop working in a "
    "future version. Please adjust your imports.",
    DeprecationWarning
)
