# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.validators import EmailValidator


class EmailValidatorTest:
    @staticmethod
    @pytest.mark.xfail(reason='EmailValidator not implemented yet')
    def test_email_validator_not_implemented_error():
        EmailValidator()
