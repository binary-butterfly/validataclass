# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

# "Meta exceptions" (not validation errors, but logic errors in the code, e.g. when specifying invalid options for a validator)
from .meta_exceptions import InvalidValidatorOptionException, DataclassValidatorFieldException

# Base and common validation error exceptions (base class ValidationError)
from .common_exceptions import ValidationError, InternalValidationError, InvalidTypeError, RequiredValueError

# More specific validation errors
from .dataclass_exceptions import DataclassPostValidationError
from .datetime_exceptions import InvalidDateError, InvalidTimeError, InvalidDateTimeError, DateTimeRangeError
from .dict_exceptions import DictFieldsValidationError, DictInvalidKeyTypeError, DictRequiredFieldError
from .list_exceptions import ListItemsValidationError, ListLengthError
from .misc_exceptions import ValueNotAllowedError
from .number_exceptions import NumberRangeError, DecimalPlacesError, InvalidDecimalError, NonFiniteNumberError
from .regex_exceptions import RegexMatchError
from .string_exceptions import StringInvalidLengthError, StringTooShortError, StringTooLongError
from .url_exceptions import InvalidUrlError
