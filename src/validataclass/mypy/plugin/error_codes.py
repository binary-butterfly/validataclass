"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Final

from mypy.errorcodes import ErrorCode

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
