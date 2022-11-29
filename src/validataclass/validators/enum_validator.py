"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from enum import Enum, EnumMeta
from typing import Any, Generic, Iterable, Optional, Type, TypeVar, Union

from validataclass.exceptions import InvalidValidatorOptionException, ValueNotAllowedError
from .any_of_validator import AnyOfValidator

__all__ = [
    'EnumValidator',
    'T_Enum',
]

# Type variable for type hints in EnumValidator
T_Enum = TypeVar('T_Enum', bound=Enum)


class EnumValidator(Generic[T_Enum], AnyOfValidator):
    """
    Validator that uses an Enum class to parse input values to members of that enumeration.

    This validator is based on the `AnyOfValidator`, using the Enum the get the list of allowed values and additionally
    converting the raw values to Enum members after validation.

    By default all values in the Enum are accepted as input. This can be optionally restricted by specifying the
    `allowed_values` parameter, which will override the list of allowed values. This parameter can be specified using
    any iterable, not just as a list.

    If you just want to disallow certain values without manually specifying all of the allowed values, you can use the
    `allowed_values` parameter with some set magic, for example: `allowed_values=set(MyEnum) - {MyEnum.BadValue}`.

    The types allowed for input data will be automatically determined from the allowed Enum values by default, unless
    explicitly specified with the parameter `allowed_types`.

    By default, strings will be matched *case-insensitively*. To change this, set `case_sensitive=True`.

    NOTE: Prior to version 0.8.0, the validator was NOT case-insensitive by default. The old parameter "case_insensitive"
    still exists for compatibility, but is deprecated now and will be removed in a future version.

    If the input value is not valid (but has the correct type), a ValueNotAllowedError (code='value_not_allowed') will
    be raised. This error will include the list of allowed values (as "allowed_values"), as long as this list is not
    longer than 20 items. (See `AnyOfValidator`.)

    Examples:

    ```
    EnumValidator(ExampleEnum)

    # Only allow strings as input, regardless of the enum's values
    EnumValidator(ExampleEnum, allowed_types=[str])

    # Only allow values explicitly specified (as long as they are valid values of the Enum)
    EnumValidator(ExampleEnum, allowed_values=['foo', 'bar'])

    # Same as above, but by specifying Enum members instead of their values (given that ExampleEnum.FOO = 'foo', ExampleEnum.BAR = 'bar')
    EnumValidator(ExampleEnum, allowed_values=[ExampleEnum.FOO, ExampleEnum.BAR])

    # Allow all Enum values except for 'foo' without specifying all allowed values explicitly
    EnumValidator(ExampleEnum, allowed_values=set(ExampleEnum) - {ExampleEnum.FOO})
    ```

    Valid input: Values of the Enum members
    Output: Member of specified Enum class
    """

    # Enum class used to determine the list of allowed values
    enum_cls: Type[Enum]

    # TODO: For version 1.0, remove the old parameter "case_insensitive" completely and set a real default value for the
    #  new "case_sensitive" parameter. (See base AnyOfValidator.)
    def __init__(
        self,
        enum_cls: Type[Enum],
        *,
        allowed_values: Optional[Iterable[Any]] = None,
        allowed_types: Optional[Union[type, Iterable[type]]] = None,
        case_sensitive: Optional[bool] = None,
        case_insensitive: Optional[bool] = None,
    ):
        """
        Create a EnumValidator for a specified Enum class, optionally with a restricted list of allowed values.

        Parameters:
            enum_cls: Enum class to use for validation (required)
            allowed_values: List (or iterable) of values from the Enum that are accepted (default: None, all Enum values allowed)
            allowed_types: List (or iterable) of types allowed for input data (default: None, autodetermine types from enum values)
            case_sensitive: If set, strings will be matched case-sensitively (default: True)
            case_insensitive: DEPRECATED. Validator is case-insensitive by default, use case_sensitive to change this.
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
            any_of_values = [value for value in allowed_values if value in enum_values]
        else:
            any_of_values = enum_values

        # Initialize base AnyOfValidator
        super().__init__(
            allowed_values=any_of_values,
            allowed_types=allowed_types,
            case_sensitive=case_sensitive,
            case_insensitive=case_insensitive,
        )

    def validate(self, input_data: Any, **kwargs) -> T_Enum:
        """
        Validate input to be a valid value of the specified Enum. Returns the Enum member.
        """
        # Validate input using the AnyOfValidator first
        input_data = super().validate(input_data, **kwargs)

        # Try to convert value to enum member
        try:
            return self.enum_cls(input_data)
        except ValueError:
            # This case should never happen, since only valid enum values are accepted by the AnyOfValidator
            raise ValueNotAllowedError()
