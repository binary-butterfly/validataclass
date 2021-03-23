# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import BooleanField


class BooleanDictInput(DictInput):
    test_field = BooleanField()


class BooleanFieldTest(TestCase):
    def test_valid_true(self):
        form = BooleanDictInput(data={'test_field': True})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': True}

    def test_valid_false(self):
        form = BooleanDictInput(data={'test_field': False})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': False}

    def test_invalid(self):
        form = BooleanDictInput(data={'test_field': 1})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}
