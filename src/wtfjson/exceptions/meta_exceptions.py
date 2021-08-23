# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

__all__ = [
    'InvalidValidatorOptionException',
    'DataclassValidatorFieldException',
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
    Exception that is raised at creation of a validator_dataclass or a DataclassValidator when a field of the dataclass does not
    match the requirements. For example if no validator is specified for a field, or an object of invalid type is specified as
    in the field metadata.

    (This is not an input validation error.)
    """
    pass
