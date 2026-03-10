"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Final

# Built-in decorators that turn a class into a validataclass.
# Use `PluginConfig.custom_validataclass_decorators` to get user-defined decorators from the plugin config.
VALIDATACLASS_DECORATORS: Final = {
    'validataclass.dataclasses.validataclass.validataclass',
}

# Built-in functions that create validataclass fields.
# Use `PluginConfig.custom_field_functions` to get user-defined field functions from the plugin config.
VALIDATACLASS_FIELD_FUNCS: Final = {
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
