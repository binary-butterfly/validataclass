# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum, EnumMeta
from typing import Any, Type, Union, List

from .any_of_validator import AnyOfValidator
from wtfjson.exceptions import InvalidValidatorOptionException, ValueNotAllowedError

__all__ = [
    'EnumValidator',
]


class EnumValidator(AnyOfValidator):
    """
    Validator that uses an Enum class to parse input values to members of that enumeration.

    This validator is based on the `AnyOfValidator`, using the Enum the get the list of allowed values and additionally converting the
    raw values to Enum members after validation.

    By default all values in the Enum are accepted as input. This can be optionally restricted by specifying the 'allowed_values'
    parameter, which will override the list of allowed values. Values in this list that are not valid for the Enum will be silently
    ignored though.

    The types allowed for input data will be automatically determined from the allowed Enum values by default, unless explicitly
    specified with the parameter 'allowed_types'.

    Examples:

    ```
    EnumValidator(ExampleEnum)

    # Only allow strings as input, regardless of the enum's values
    EnumValidator(ExampleEnum, allowed_types=[str])

    # Only allow values explicitly specified (as long as they are valid values of the Enum)
    EnumValidator(ExampleEnum, allowed_values=['foo', 'bar'])

    # Same as above, but by specifying Enum members instead of their values (given that ExampleEnum.FOO = 'foo', ExampleEnum.BAR = 'bar')
    EnumValidator(ExampleEnum, allowed_values=[ExampleEnum.FOO, ExampleEnum.BAR])
    ```

    Valid input: Values of the Enum members
    Output: Member of specified Enum class
    """

    # Enum class used to determine the list of allowed values
    enum_cls: Type[Enum]

    def __init__(self, enum_cls: Type[Enum], *, allowed_values: List[Any] = None, allowed_types: Union[type, List[type]] = None):
        """
        Create a EnumValidator for a specified Enum class, optionally with a restricted list of allowed values.

        Parameters:
            enum_cls: Enum class to use for validation (required)
            allowed_values: List of values from the Enum that are accepted as input (default: None, all Enum values allowed)
            allowed_types: List of types allowed for input data (default: None, autodetermine types from enum values)
        """
        # Ensure parameter is an Enum class
        if not isinstance(enum_cls, EnumMeta):
            raise InvalidValidatorOptionException('Parameter "enum_cls" must be an Enum class.')

        self.enum_cls = enum_cls

        # Get all values from Enum
        enum_values = [member.value for member in enum_cls]

        # If allowed_values parameter is given, restrict the enum values to those that are present in allowed_values
        if allowed_values is not None:
            # Replace Enum members in allowed_values with their actual values
            allowed_values = [item.value if isinstance(item, Enum) else item for item in allowed_values]
            any_of_values = [value for value in enum_values if value in allowed_values]
        else:
            any_of_values = enum_values

        # Initialize base AnyOfValidator
        super().__init__(allowed_values=any_of_values, allowed_types=allowed_types)

    def validate(self, input_data: Any) -> Enum:
        """
        Validate input to be a valid value of the specified Enum. Returns the Enum member.
        """
        # Validate input using the AnyOfValidator first
        input_data = super().validate(input_data)

        # Try to convert value to enum member
        try:
            return self.enum_cls(input_data)
        except ValueError:
            # This case should never happen, since only valid enum values are accepted by the AnyOfValidator
            raise ValueNotAllowedError()
