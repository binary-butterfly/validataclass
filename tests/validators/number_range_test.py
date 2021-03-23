# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import IntegerField
from wtfjson.validators import NumberRange


class NumberRangeDictInput(DictInput):
    test_field = IntegerField(
        validators=[
            NumberRange(min=5, max=10)
        ]
    )


class NumberRangeTest(TestCase):
    def test_success_min(self):
        form = NumberRangeDictInput(data={'test_field': 5})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 5}

    def test_success_max(self):
        form = NumberRangeDictInput(data={'test_field': 10})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 10}

    def test_invalid_type(self):
        form = NumberRangeDictInput(data={'test_field': 'cookie'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_invalid_value_min(self):
        form = NumberRangeDictInput(data={'test_field': 2})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid length']}

    def test_invalid_value_max(self):
        form = NumberRangeDictInput(data={'test_field': 20})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid length']}
