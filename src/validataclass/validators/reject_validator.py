"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional, Type

from validataclass.exceptions import ValidationError, FieldNotAllowedError
from .validator import Validator

__all__ = [
    'RejectValidator',
]


class RejectValidator(Validator):
    """
    Special validator that rejects any input data with a validation error.

    This validator can be used for example in dataclasses to define a field that may never be set, or to override an
    existing field in a subclassed dataclass that may not be set in this subclass. Keep in mind that in a dataclass
    you still need to define a default value for this field, e.g. with `DefaultUnset` or `Default(None)`, otherwise you
    have a dataclass with a field that is required but can never be valid.

    By default, the validator literally rejects anything. In some cases you may want to allow `None` as the only valid
    input value. This can be done by setting the parameter `allow_none=True`. In that case, the validator returns `None`
    if `None` is the input value, and rejects anything else.

    The validator raises a `FieldNotAllowedError` by default. Optionally you can set a custom exception class using
    the parameter `error_class` (must be a subclass of `ValidationError`). There are also the parameters `error_code`
    to override the default error code with a custom one, and `error_reason` to specify a detailed error message for
    the user.

    Examples:

    ```
    # Rejects any input with a FieldNotAllowedError (including None)
    RejectValidator()

    # Accepts None as the only value, rejects anything else with a FieldNotAllowedError
    RejectValidator(allow_none=True)

    # Set custom error codes and reasons (but still raises FieldNotAllowedError exceptions)
    RejectValidator(error_code='custom_error_code')
    RejectValidator(error_reason='This field cannot be changed.')

    # Set a custom error class (will raise this exception with its default error code on error)
    class CustomValidationError(ValidationError):
        code = 'custom_error_code'

    RejectValidator(error_class=CustomValidationError)
    RejectValidator(error_class=CustomValidationError, error_code='other_error_code')
    RejectValidator(error_class=CustomValidationError, error_reason='This field cannot be changed.')
    ```

    Valid input: Nothing (`None` if allow_none=True)
    Output: Never returns (`None` if allow_none=True)
    """

    # Whether to allow None as the only valid input
    allow_none: bool

    # Validation error to raise when rejecting input
    error_class: Type[ValidationError]
    error_code: Optional[str]
    error_reason: Optional[str]

    def __init__(
        self, *,
        allow_none: bool = False,
        error_class: Type[ValidationError] = FieldNotAllowedError,
        error_code: Optional[str] = None,
        error_reason: Optional[str] = None,
    ):
        """
        Create a RejectValidator that rejects any input.

        Parameters:
            allow_none: `bool`, if True, the validator excepts `None` as the only valid input (default: False)
            error_class: Subclass of `ValidationError` that is raised by the validator (default: `FieldNotAllowedError`)
            error_code: `str`, optionally overrides the default error code of the error class (default: None)
            error_reason: `str`, optionally sets the "reason" field in the error class (default: None)
        """
        # Check parameter validity
        if not issubclass(error_class, ValidationError):
            raise TypeError('Error class must be a subclass of ValidationError.')

        # Save parameters
        self.allow_none = allow_none
        self.error_class = error_class
        self.error_code = error_code
        self.error_reason = error_reason

    def validate(self, input_data: Any) -> None:
        """
        Validate input data. In this case, reject any value (except for `None` if allow_none is set).
        """
        # Accept None (if allowed)
        if self.allow_none and input_data is None:
            return None

        # Reject any input
        raise self.error_class(code=self.error_code, reason=self.error_reason)
