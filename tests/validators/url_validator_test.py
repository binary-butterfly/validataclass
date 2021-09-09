# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.validators import UrlValidator


class UrlValidatorTest:
    @staticmethod
    @pytest.mark.xfail(reason='UrlValidator not implemented yet')
    def test_url_validator_not_implemented_error():
        UrlValidator()
