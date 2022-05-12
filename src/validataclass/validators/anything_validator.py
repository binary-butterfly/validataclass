"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional, Union, List, Iterable

from validataclass.exceptions import InvalidValidatorOptionException
from .validator import Validator

__all__ = [
    'AnythingValidator',
]


class AnythingValidator(Validator):
    """
    Special validator that accepts any input without validation.

    This validator can be used in places where it's not possible or necessary to validate the input but where the input
    should still be preserved (e.g. as a field in a dataclass), or where the unvalidated data should be saved and
    properly validated at a later point.

    By default this validator accepts literally anything, including `None`. There are two optional parameters which can
    be used to restrict the validator to some extend: `allow_none` and `allowed_types`.

    To reject `None` as input, but accept anything else, you can set `allow_none=False`.

    To only allow a certain set of input data types, you can set `allowed_types` to a list or set (or any iterable) of
    types. The validator will do a type check on the input data then and reject any types that are not part of
    `allowed_types`. Keep in mind that no further validation will be performed on the data.

    Setting `allowed_types` will also cause the validator to reject `None` unless it is part of the allowed types. For
    example, if you set `allowed_types=[str]`, only strings will be accepted. If you additionally want to allow `None`,
    you can set `allow_none=True`. Alternatively you can also specify `type(None)` or `None` in the allowed types list.

    The validation errors raised by this validator are `RequiredValueError` (only if `allow_none=False` or
    `allowed_types` is used) and `InvalidTypeError` (only if `allowed_types` is used).

    Examples:

    ```
    # Accepts any input and returns it unmodified (including None)
    AnythingValidator()

    # Accepts any input except for None (which raises a RequiredValueError)
    AnythingValidator(allow_none=False)

    # Accepts only integers and floats, which are returned unmodified (None is not allowed)
    AnythingValidator(allowed_types=[int, float])

    # Accepts only None and dictionaries (which are returned completely unvalidated!)
    AnythingValidator(allowed_types=[dict], allow_none=True)
    AnythingValidator(allowed_types=[dict, type(None)])  # same as above
    AnythingValidator(allowed_types=[dict, None])        # same as above, allowed as a shortcut
    ```

    Valid input: Anything (unless restricted by the parameters)
    Output: Unmodified input
    """

    # Whether to allow None as input
    allow_none: bool

    # Which input types to allow (None for anything)
    allowed_types: Optional[List[type]]

    def __init__(
        self, *,
        allow_none: Optional[bool] = None,
        allowed_types: Optional[Union[Iterable[Union[type, None]], type]] = None,
    ):
        """
        Create an AnythingValidator that accepts any input.

        The optional `allowed_types` parameter can be specified as any iterable of types (e.g. a list of types). As a
        convenience, a single type can be specified as well (e.g. `allowed_types=[dict]` and `allowed_types=dict` are
        equivalent).

        The default of the `allow_none` parameter depends on whether `allowed_types` is set. If it's not set, anything
        should be valid input, including None, so the default is True. If `allowed_types` is set, `allow_none` will
        default to True if `type(None)` is part of `allowed_types`, and False otherwise.

        If you set both `allow_none` and `allowed_types` explicitly, `allow_none` takes precedence. This means that if
        you set `allow_none=True`, `type(None)` will be automatically added to `allowed_types`. If you set it to False,
        the NoneType will be automatically removed from `allowed_types` (if it was specified in the first place).

        Parameters:
            allow_none: Boolean, whether to allow None as the input value (default: depends on context, see above)
            allowed_types: One or multiple types, specifies which input types are allowed (default: None, allow any type)
        """
        # Normalize list of allowed types (remove duplicates, replace None with type(None), etc.)
        if allowed_types is not None:
            allowed_types = self._normalize_allowed_types(allowed_types=allowed_types, allow_none=allow_none)

        # The default value for allow_none depends on whether allowed_types are specified. If yes, allow_none is
        # auto-determined from the list of allowed types (whether it includes NoneType), otherwise allow_none is True.
        if allow_none is None:
            allow_none = type(None) in allowed_types if allowed_types is not None else True

        # Save parameters
        self.allow_none = allow_none
        self.allowed_types = allowed_types

    @staticmethod
    def _normalize_allowed_types(
        *,
        allowed_types: Optional[Union[Iterable[Union[type, None]], type]],
        allow_none: Optional[bool],
    ) -> List[type]:
        """
        Helper method to normalize the allowed_types parameter to a unique list that contains only types.
        """
        # If allowed_types is not already an Iterable, put it in a list. (Treating strings as iterable doesn't make sense
        # here, so we make an exception for strings to give the user a more meaningful error messsage in the next step.)
        if not isinstance(allowed_types, Iterable) or type(allowed_types) is str:
            allowed_types = [allowed_types]

        # Make sure allowed_types only contains valid types (or None, which is replaced later)
        for t in allowed_types:
            if type(t) is not type and t is not None:
                raise InvalidValidatorOptionException(f'Element of allowed_types is not a type: {t!r}')

        # Convert to a set to remove duplicates and replace None with NoneType while we're on it
        allowed_types = set(type(None) if t is None else t for t in allowed_types)

        # If allow_none is set, this parameter overrides whether NoneType is part of the allowed types
        if allow_none is True:
            allowed_types.add(type(None))
        elif allow_none is False:
            allowed_types.discard(type(None))

        # Don't allow empty allowed_types
        if len(allowed_types) == 0:
            raise InvalidValidatorOptionException('allowed_types is empty. Use the RejectValidator instead.')

        return list(allowed_types)

    def validate(self, input_data: Any) -> Any:
        """
        Validate input data. Accepts anything (or only specific types) and returns data unmodified.
        """
        # Accept None (if allowed explicitly with allow_none=True or implicitly with NoneType in allowed_types)
        if self.allow_none and input_data is None:
            return None

        # If allowed_types is set, do a type check (this also raises a RequiredValueError if the input is None)
        if self.allowed_types is not None:
            self._ensure_type(input_data, self.allowed_types)
        else:
            # No type restrictions, but we still need to check for None (the allow_none=True case is already covered above)
            self._ensure_not_none(input_data)

        # Return input unmodified
        return input_data
