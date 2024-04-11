"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

__all__ = [
    'InvalidValidatorOptionException',
    'DataclassValidatorFieldException',
    'DataclassInvalidPreValidateSignatureException',
]


# These are "meta exceptions" that are not validation errors, but rather logic errors in the code.
# For example when creating a validator with invalid options.

class InvalidValidatorOptionException(ValueError):
    """
    Exception that is raised when attempting to create a validator with invalid options (e.g. setting two options that are
    mutually exclusive).

    (This is not an input validation error.)
    """
    pass


class DataclassValidatorFieldException(Exception):
    """
    Exception that is raised at creation of a dataclass with `@validataclass` or at creation of a `DataclassValidator` when a field of
    the dataclass does not match the requirements. For example if no validator is specified for a field, or an object of invalid type is
    specified as in the field metadata.

    (This is not an input validation error.)
    """
    pass


class DataclassInvalidPreValidateSignatureException(Exception):
    """
    Exception that is raised by the DataclassValidator when used with a dataclass that has a `__pre_validate__()` method
    with an invalid method signature (i.e. not enough or too many positional arguments.)

    (This is not an input validation error.)
    """
    pass
