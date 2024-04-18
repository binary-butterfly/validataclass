"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

# "Meta exceptions" (no validation errors, but logic errors in the validators, e.g. when specifying invalid options for
# a validator)
from .meta_exceptions import (
    DataclassInvalidPreValidateSignatureException,
    DataclassValidatorFieldException,
    InvalidValidatorOptionException,
)

# Base exception classes for validation errors
from .base_exceptions import ValidationError

# Common validation errors used throughout the library
from .common_exceptions import RequiredValueError, FieldNotAllowedError, InvalidTypeError

# More specific validation errors
from .dataclass_exceptions import DataclassPostValidationError
from .datetime_exceptions import InvalidDateError, InvalidTimeError, InvalidDateTimeError, DateTimeRangeError
from .dict_exceptions import DictFieldsValidationError, DictInvalidKeyTypeError, DictRequiredFieldError
from .email_exceptions import InvalidEmailError
from .list_exceptions import ListItemsValidationError, ListLengthError
from .misc_exceptions import ValueNotAllowedError
from .number_exceptions import (
    DecimalPlacesError,
    InvalidDecimalError,
    InvalidIntegerError,
    NonFiniteNumberError,
    NumberRangeError,
)
from .regex_exceptions import RegexMatchError
from .string_exceptions import (
    StringInvalidCharactersError,
    StringInvalidLengthError,
    StringTooLongError,
    StringTooShortError,
)
from .url_exceptions import InvalidUrlError
