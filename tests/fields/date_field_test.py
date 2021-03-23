# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date
from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import DateField


class DateDictInput(DictInput):
    test_field = DateField()


class DateFieldTest(TestCase):
    def test_success(self):
        form = DateDictInput(data={'test_field': '2020-10-01'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': date(2020, 10, 1)}

    def test_invalid_type(self):
        form = DateDictInput(data={'test_field': 1})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_invalid_format(self):
        form = DateDictInput(data={'test_field': '2020-20-33'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid date']}

    def test_invalid_date(self):
        form = DateDictInput(data={'test_field': '2020-20-33'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid date']}
