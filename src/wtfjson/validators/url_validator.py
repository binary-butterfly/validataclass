# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from .string_validator import StringValidator

__all__ = [
    'UrlValidator',
]


class UrlValidator(StringValidator):
    """
    Validator for URLs.

    TODO: To be implemented in version 1.0.0 (or earlier)!
    """

    def __init__(self):
        super().__init__()
        raise NotImplementedError()
