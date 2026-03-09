"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Final

# Decorators that turn a class to a validataclass
# (Not Final so it can be modified by other plugins that add their own validataclass-style decorators.)
VALIDATACLASS_DECORATORS = {
    'validataclass.dataclasses.validataclass.validataclass',
}

# Functions that create validataclass fields (must have similar signature as validataclass_field)
VALIDATACLASS_FIELD_FUNCS = {
    'validataclass.dataclasses.validataclass_field.validataclass_field',
}

# Full name of base class for validators
VALIDATOR_BASE_CLASS: Final = 'validataclass.validators.validator.Validator'

# Full name of base class for default objects
FIELD_DEFAULT_BASE_CLASS: Final = 'validataclass.dataclasses.defaults.BaseDefault'

# Full and short name of the virtual field wrapper function
# NOTE: This function does not actually exist in the code, it only exists for mypy.
VIRTUAL_FIELD_WRAPPER_FUNC: Final = 'validataclass.mypy._virtual_field_wrapper'
VIRTUAL_FIELD_WRAPPER_FUNC_NAME: Final = '_virtual_field_wrapper'
