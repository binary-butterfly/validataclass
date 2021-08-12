# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""


# These are "meta exceptions" that are not validation errors, but rather logic errors in the code.
# For example when creating a validator with invalid options.

class InvalidValidatorOptionException(ValueError):
    """
    Exception that is raised when attempting to create a validator with invalid options (e.g. setting two options
    that are mutually exclusive).

    (This is not an input validation error.)
    """
    pass


class DataclassInvalidFieldValidatorException(Exception):
    """
    Exception that is raised at creation of a DataclassValidator when a field of the dataclass does not have a valid
    Validator associated with it (e.g. if no Validator was specified, or the 'validator' metadata contains something
    that is not a Validator object).

    (This is not an input validation error.)
    """
    pass
