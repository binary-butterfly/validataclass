# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import StringField
from wtfjson.validators import AnyOf


class AnyOfStringDictInput(DictInput):
    test_field = StringField(
        validators=[
            AnyOf(['cookie', 'vanilla'])
        ]
    )


class AnyOfTest(TestCase):
    def test_success(self):
        form = AnyOfStringDictInput(data={'test_field': 'cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 'cookie'}

    def test_invalid_type(self):
        form = AnyOfStringDictInput(data={'test_field': 12})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_invalid_value(self):
        form = AnyOfStringDictInput(data={'test_field': 'chocolate'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['is not in any-of list']}
