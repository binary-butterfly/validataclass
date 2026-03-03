"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from mypy.types import Instance
from typing_extensions import Self


class ParsedValidataclassField:
    """
    Internal representation of the types of a parsed validataclass field.
    """

    # True if there was an error while analyzing the field
    error: bool = False

    # If None, the field does not have an explicit validator/default, but could still have one from the base class.
    validator_type: Instance | None = None
    default_type: Instance | None = None

    def merge(self, other: Self) -> None:
        """
        Merge another instance of this class into this one.
        Validator type and default object type are replaced if the attributes in the other instance are not None.
        The error flag is set to True if it's true for any instance.
        """
        self.error = self.error or other.error

        if other.validator_type is not None:
            self.validator_type = other.validator_type
        if other.default_type is not None:
            self.default_type = other.default_type


class ParsedFieldCache:
    """
    Cache for ParsedValidataclassFields, i.e. the parsed validator and default types of a validataclass field.

    This cache is globally shared for the entire plugin, meaning that all VirtualFieldResolver instances can access it.
    It's used to store the result of the field resolver, so that later instances can access the parsed types of a field
    in a base class.

    Important: This cache is NOT related to the mypy cache. It is also NOT persisted across multiple mypy runs.
    (Although it is possible that we might persist the cache in a future release to speed up continuous runs of mypy.)
    """

    # Nested dictionary, outer key is the fully qualified name of a validataclass, inner key is the name of a field,
    # values are objects representing parsed validataclass fields.
    _fields: dict[str, dict[str, ParsedValidataclassField]]

    def __init__(self) -> None:
        self._fields = {}

    def get_field(self, class_name: str, field_name: str) -> ParsedValidataclassField:
        """
        Retrieve a parsed validataclass field for a given field in a given class from the cache.

        The class and field must exist in the cache, otherwise a KeyError is raised.
        """
        return self._fields[class_name][field_name]

    def set_field(self, class_name: str, field_name: str, parsed_field: ParsedValidataclassField) -> None:
        """
        Store a parsed validataclass field in the cache.
        """
        class_fields = self._fields.setdefault(class_name, {})
        class_fields[field_name] = parsed_field
