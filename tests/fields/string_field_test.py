# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import StringField


class StringDictInput(DictInput):
    test_field = StringField()


class StringFieldTest(TestCase):
    def test_success(self):
        form = StringDictInput(data={'test_field': 'string'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 'string'}

    def test_invalid(self):
        form = StringDictInput(data={'test_field': 20})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}
