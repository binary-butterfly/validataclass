"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
import warnings

from validataclass.helpers import UnsetValue

__all__ = [
    'ValidataclassMixin',
]


class ValidataclassMixin:
    """
    Mixin class for validataclasses that provides some commonly used methods like `to_dict()`.

    Example:

    ```
    @validataclass
    class ExampleClass(ValidataclassMixin):
        pass
    ```
    """

    def to_dict(self, *, keep_unset_values: bool = False) -> dict:
        """
        Returns the data of the object as a dictionary (recursively resolving inner dataclasses as well).

        Filters out all fields with `UnsetValue`, unless the optional parameter `keep_unset_values` is True.

        Parameters:
            keep_unset_values: If true, fields with value `UnsetValue` are NOT removed from the dictionary (default: False)
        """
        data = dataclasses.asdict(self)  # noqa

        # Filter out all UnsetValues (unless said otherwise)
        if not keep_unset_values:
            data = {key: value for key, value in data.items() if value is not UnsetValue}

        return data

    @classmethod
    def create_with_defaults(cls, **kwargs):
        """
        (Deprecated.) Creates an object of the dataclass (with its default values).

        Since version 0.6.0, this method is no longer necessary and therefore deprecated. You can now use the regular
        dataclass constructor, e.g. `MyDataclass(foo=42)` instead of `MyDataclass.create_with_defaults(foo=42)`.

        This method will be removed in a future version (presumably in version 1.0.0).
        """
        warnings.warn(
            "create_with_defaults() is deprecated and will be removed in a future version. To instantiate a validataclass, "
            "you can now use the regular constructor, e.g. `MyDataclass(...)` instead of `MyDataclass.create_with_defaults(...)`.",
            DeprecationWarning
        )
        return cls(**kwargs)  # noqa
