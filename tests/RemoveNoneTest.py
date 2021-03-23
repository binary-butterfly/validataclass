# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import StringField


class RemoveNoneDictInput(DictInput):
    test_field = StringField(required=False)
    keep_field = StringField(required=False)


class RemoveNoneTest(TestCase):
    def test_success(self):
        form = RemoveNoneDictInput(data={'test_field': None, 'keep_field': 'test'}, remove_none=True)
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'keep_field': 'test'}

    def test_invalid(self):
        form = RemoveNoneDictInput(data={'test_field': None})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}
