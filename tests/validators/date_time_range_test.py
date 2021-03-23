# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from time import sleep
from unittest import TestCase
from datetime import datetime, timedelta

from wtfjson import DictInput
from wtfjson.fields import DateTimeField
from wtfjson.validators import DateTimeRange


class DateTimeRangeFixedInput(DictInput):
    test_field = DateTimeField(
        accept_utc=True,
        validators=[
            DateTimeRange(
                minus=timedelta(minutes=-5),
                plus=timedelta(minutes=5),
                orientation=datetime(2020, 1, 1, 0, 0, 0)
            )
        ]
    )


class DateTimeRangeNowInput(DictInput):
    test_field = DateTimeField(
        validators=[
            DateTimeRange(
                minus=timedelta(minutes=-5),
                plus=timedelta(minutes=5)
            )
        ]
    )


class DateTimeRangeFunctionInput(DictInput):
    test_field = DateTimeField(
        validators=[
            DateTimeRange(
                minus=timedelta(seconds=-1),
                plus=timedelta(seconds=1),
                orientation=lambda: datetime.utcnow().replace(microsecond=0) + timedelta(minutes=10)
            )
        ]
    )


class DateTimeRangeTest(TestCase):
    def test_invalid_type(self):
        form = DateTimeRangeFixedInput(data={'test_field': 12})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_success_fixed(self):
        form = DateTimeRangeFixedInput(data={'test_field': '2020-01-01T00:00:00'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': datetime(2020, 1, 1, 0, 0, 0)}

    def test_success_fixed_with_z(self):
        form = DateTimeRangeFixedInput(data={'test_field': '2020-01-01T00:00:00Z'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': datetime(2020, 1, 1, 0, 0, 0)}

    def test_invalid_value_min_fixed(self):
        form = DateTimeRangeFixedInput(data={'test_field': '2020-01-01T00:10:00'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['datetime out of range']}

    def test_invalid_value_max_fixed(self):
        form = DateTimeRangeFixedInput(data={'test_field': '2020-01-01T00:10:00'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['datetime out of range']}

    def test_success_now(self):
        now = datetime.utcnow().replace(microsecond=0)
        form = DateTimeRangeNowInput(data={'test_field': now.strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': now}

    def test_invalid_value_min_now(self):
        now = datetime.utcnow()
        form = DateTimeRangeNowInput(data={'test_field': (now + timedelta(minutes=-10)).strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['datetime out of range']}

    def test_invalid_value_max_now(self):
        now = datetime.utcnow()
        form = DateTimeRangeNowInput(data={'test_field': (now + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['datetime out of range']}

    def test_success_function(self):
        now = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=10)
        form = DateTimeRangeFunctionInput(data={'test_field': now.strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': now}

    def test_success_function_wait(self):
        # TODO aaaaaa
        sleep(1.5)
        now = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=10)
        form = DateTimeRangeFunctionInput(data={'test_field': now.strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': now}

    def test_invalid_value_min_function(self):
        now = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=10)
        form = DateTimeRangeFunctionInput(data={'test_field': (now + timedelta(minutes=-10)).strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['datetime out of range']}

    def test_invalid_value_max_function(self):
        now = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=10)
        form = DateTimeRangeFunctionInput(data={'test_field': (now + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S')})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['datetime out of range']}
