"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

# Abstract base class (needs to be imported first to avoid import loops)
from .validator import Validator  # isort:skip

# Validators
from .allow_empty_string import AllowEmptyString
from .any_of_validator import AnyOfValidator
from .anything_validator import AnythingValidator
from .big_integer_validator import BigIntegerValidator
from .boolean_validator import BooleanValidator
from .dataclass_validator import DataclassValidator
from .date_validator import DateValidator
from .datetime_validator import DateTimeFormat, DateTimeValidator
from .decimal_validator import DecimalValidator
from .dict_validator import DictValidator
from .discard_validator import DiscardValidator
from .email_validator import EmailValidator
from .enum_validator import EnumValidator
from .float_to_decimal_validator import FloatToDecimalValidator
from .float_validator import FloatValidator
from .integer_validator import IntegerValidator
from .list_validator import ListValidator
from .none_to_unset_value import NoneToUnsetValue
from .noneable import Noneable
from .numeric_validator import NumericValidator
from .regex_validator import RegexValidator
from .reject_validator import RejectValidator
from .string_validator import StringValidator
from .time_validator import TimeFormat, TimeValidator
from .url_validator import UrlValidator

# Using the following TypeVars outside of the modules they were defined in is deprecated. You should define your own
# TypeVars if needed. They are still imported here for compatibility, but they won't be exported in __all__, so that
# linting tools will complain about it.
# TODO: Deprecated. Remove imports in future version.
from .dataclass_validator import T_Dataclass  # noqa  # isort:skip
from .enum_validator import T_Enum  # noqa  # isort:skip
from .list_validator import T_ListItem  # noqa  # isort:skip

__all__ = [
    'AllowEmptyString',
    'AnyOfValidator',
    'AnythingValidator',
    'BigIntegerValidator',
    'BooleanValidator',
    'DataclassValidator',
    'DateTimeFormat',
    'DateTimeValidator',
    'DateValidator',
    'DecimalValidator',
    'DictValidator',
    'DiscardValidator',
    'EmailValidator',
    'EnumValidator',
    'FloatToDecimalValidator',
    'FloatValidator',
    'IntegerValidator',
    'ListValidator',
    'NoneToUnsetValue',
    'Noneable',
    'NumericValidator',
    'RegexValidator',
    'RejectValidator',
    'StringValidator',
    'TimeFormat',
    'TimeValidator',
    'UrlValidator',
    'Validator',
]
