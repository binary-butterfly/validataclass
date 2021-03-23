# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from unittest import TestCase

from wtfjson import DictInput
from wtfjson.fields import StringField
from wtfjson.validators import Regexp


class RegexpPatternDictInput(DictInput):
    test_field = StringField(
        validators=[
            Regexp(re.compile(r'\d+\w+'))
        ]
    )


class RegexpStringDictInput(DictInput):
    test_field = StringField(
        validators=[
            Regexp(r'\d+\w+')
        ]
    )


class RegexpTest(TestCase):
    def test_success_pattern(self):
        form = RegexpPatternDictInput(data={'test_field': '1cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': '1cookie'}

    def test_success_string(self):
        form = RegexpStringDictInput(data={'test_field': '1cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': '1cookie'}

    def test_invalid_mail(self):
        form = RegexpPatternDictInput(data={'test_field': 'cookie'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['regexp failed']}
