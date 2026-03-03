"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Final

from mypy.errorcodes import ErrorCode

# Decorators that turn a class to a validataclass
# (Not Final so it can be modified by other plugins that add their own validataclass-style decorators.)
VALIDATACLASS_DECORATORS = {
    'validataclass.dataclasses.validataclass.validataclass',
}

# Full and short name of the validataclass_field()
VALIDATACLASS_FIELD_FUNC: Final = 'validataclass.dataclasses.validataclass_field.validataclass_field'
VALIDATACLASS_FIELD_FUNC_NAME: Final = 'validataclass_field'

# Full name of base class for validators
VALIDATOR_BASE_CLASS: Final = 'validataclass.validators.validator.Validator'

# Full name of base class for default objects
FIELD_DEFAULT_BASE_CLASS: Final = 'validataclass.dataclasses.defaults.BaseDefault'

# Full name of the type of the special NoDefault object
FIELD_NO_DEFAULT_CLASS: Final = 'validataclass.dataclasses.defaults._NoDefaultType'

# Full and short name of the virtual field wrapper function
# NOTE: This function does not actually exist in the code, it only exists for mypy.
VIRTUAL_FIELD_WRAPPER_FUNC: Final = 'validataclass.mypy._virtual_field_wrapper'
VIRTUAL_FIELD_WRAPPER_FUNC_NAME: Final = '_virtual_field_wrapper'

# Custom error codes for validataclass
ERROR_CODE_VALIDATACLASS: Final = ErrorCode(
    'validataclass',
    'Check that validataclasses are defined correctly',
    'Plugin',
)
ERROR_CODE_VALIDATACLASS_EMPTY_TYPE: Final = ErrorCode(
    'validataclass-empty-type',
    'Check that validataclass field has a validator or default that can return a value',
    'Plugin',
    sub_code_of=ERROR_CODE_VALIDATACLASS,
)
ERROR_CODE_VALIDATACLASS_NOT_IMPLEMENTED: Final = ErrorCode(
    'validataclass-not-implemented',
    'Special code for edge cases that are currently not supported by the plugin (please create a bug report)',
    'Plugin',
    sub_code_of=ERROR_CODE_VALIDATACLASS,
)
