# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import StringField
from wtfjson.validators import NoneOf


class NoneOfStringDictInput(DictInput):
    test_field = StringField(
        validators=[
            NoneOf(['cookie'])
        ]
    )


class NoneOfTest(TestCase):
    def test_success(self):
        form = NoneOfStringDictInput(data={'test_field': 'chocolate'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 'chocolate'}

    def test_invalid_type(self):
        form = NoneOfStringDictInput(data={'test_field': 12})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_invalid_value(self):
        form = NoneOfStringDictInput(data={'test_field': 'cookie'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['is in none-of list']}
