# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional


class ValidationError(ValueError):
    """
    will add an validation error
    """

    message: str

    def __init__(self, message: Optional[str] = None):
        self.message = message


class StopValidation(Exception):
    """
    will add an error and stop validation because more validators will run in errors
    """

    message: str

    def __init__(self, message: Optional[str] = None):
        self.message = message


class ClearValidation(Exception):
    """
    not really an exception: clears errors from validations before, usually for optional fields
    """
    pass


class NotValidated(Exception):
    """
    will be thrown if somebody tries to access data before validating
    """
    pass


class InvalidData(Exception):
    """
    will be thrown if somebody tries to access data which is not there
    """
    pass


class InvalidValidator(Exception):
    """
    will be thrown if the validator is not suitable for this type of field
    """
    pass
