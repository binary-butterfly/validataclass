"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from datetime import datetime, timedelta, timezone

import pytest
from dateutil import tz

from tests.test_utils import unpack_params
from validataclass.helpers import DateTimeRange, DateTimeOffsetRange


class TestDatetimeCallable:
    """ Callable class that returns a datetime that can be counted up or down from outside. """

    def __init__(self, start_datetime: datetime):
        self.current = start_datetime

    def __call__(self) -> datetime:
        return self.current

    def count(self, step: int) -> None:
        self.current = self.current + timedelta(seconds=step)


class DateTimeRangeTest:
    """ Tests for the DateTimeRange class. """

    @staticmethod
    @pytest.mark.parametrize(
        'input_datetime',
        [
            datetime(1900, 1, 1, 0, 0, 0),
            datetime(2021, 9, 7, 12, 34, 56),
            datetime(2999, 12, 31, 12, 34, 56, tzinfo=tz.gettz('Europe/Berlin')),
        ],
    )
    def test_range_without_boundaries(input_datetime):
        """ Test DateTimeRange without any boundaries. """
        dt_range = DateTimeRange()
        assert dt_range.contains_datetime(input_datetime) is True

    @staticmethod
    @pytest.mark.parametrize(
        'lower_boundary, upper_boundary',
        [
            # Static datetimes
            (None, None),
            (datetime(2021, 9, 8, 7, 6, 5), None),
            (None, datetime(2021, 9, 8, 7, 6, 5)),
            (datetime(2021, 9, 8, 7, 6, 5), datetime(2021, 10, 9, 8, 7, 6)),

            # Callables
            (datetime.now, lambda: datetime(2021, 9, 8, 7, 6, 5)),
        ],
    )
    def test_range_repr(lower_boundary, upper_boundary):
        """ Test DateTimeRange `__repr__()` method. """
        dt_range = DateTimeRange(
            lower_boundary=lower_boundary,
            upper_boundary=upper_boundary,
        )

        assert repr(dt_range) == f'DateTimeRange(lower_boundary={lower_boundary!r}, upper_boundary={upper_boundary!r})'

    @staticmethod
    @pytest.mark.parametrize(
        'lower_boundary, upper_boundary, expected_dict',
        [
            # Static datetimes
            (
                None,
                None,
                {},
            ),
            (
                datetime(2021, 9, 8, 7, 6, 5, tzinfo=timezone.utc),
                None,
                {'lower_boundary': '2021-09-08T07:06:05+00:00'},
            ),
            (
                None,
                datetime(2021, 9, 8, 7, 6, 5, tzinfo=timezone.utc),
                {'upper_boundary': '2021-09-08T07:06:05+00:00'},
            ),
            (
                datetime(2021, 9, 8, 7, 6, 5),
                datetime(2021, 10, 9, 8, 7, 6),
                {'lower_boundary': '2021-09-08T07:06:05', 'upper_boundary': '2021-10-09T08:07:06'},
            ),

            # Callables
            (
                lambda: datetime(2021, 9, 8, 7, 6, 5),
                lambda: datetime(2021, 9, 8, 7, 6, 5) + timedelta(hours=3),
                {'lower_boundary': '2021-09-08T07:06:05', 'upper_boundary': '2021-09-08T10:06:05'},
            ),
        ],
    )
    def test_range_to_dict(lower_boundary, upper_boundary, expected_dict):
        """ Test DateTimeRange `to_dict()` method. """
        dt_range = DateTimeRange(
            lower_boundary=lower_boundary,
            upper_boundary=upper_boundary,
        )

        assert dt_range.to_dict() == expected_dict

    @staticmethod
    def test_range_to_dict_with_local_timezone():
        """ Test DateTimeRange `to_dict()` method with local_timezone parameter. """
        dt_range = DateTimeRange(
            lower_boundary=datetime(2021, 9, 8, 7, 6, 5),
            upper_boundary=datetime(2021, 10, 9, 8, 7, 6)
        )

        assert dt_range.to_dict(local_timezone=timezone(timedelta(hours=3))) == {
            'lower_boundary': '2021-09-08T07:06:05+03:00',
            'upper_boundary': '2021-10-09T08:07:06+03:00'
        }

    # Tests for different boundary options (static/callable) with all datetimes having timezones

    @staticmethod
    @pytest.mark.parametrize(
        'lower_boundary, upper_boundary, input_datetime, expected_result',
        [
            # Lower boundary only
            *unpack_params(
                datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                None,
                [
                    (datetime(1900, 1, 1, 12, 34, 56, tzinfo=timezone.utc), False),
                    (datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(microseconds=1), False),
                    (datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2021, 9, 7, 12, 34, 56, tzinfo=timezone.utc), True),
                    (datetime(2999, 12, 31, 23, 59, 59, tzinfo=timezone.utc), True),
                ],
            ),

            # Upper boundary only
            *unpack_params(
                None,
                datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                [
                    (datetime(1900, 1, 1, 12, 34, 56, tzinfo=timezone.utc), True),
                    (datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2000, 1, 1, 0, 0, 0, microsecond=1, tzinfo=timezone.utc), False),
                    (datetime(2021, 9, 7, 12, 34, 56, tzinfo=timezone.utc), False),
                    (datetime(2999, 12, 31, 23, 59, 59, tzinfo=timezone.utc), False),
                ],
            ),

            # Lower and upper boundary
            *unpack_params(
                datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                datetime(2019, 12, 31, 23, 59, 59, microsecond=999999, tzinfo=timezone.utc),
                [
                    (datetime(1900, 1, 1, 12, 34, 56, tzinfo=timezone.utc), False),
                    (datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2016, 7, 28, 12, 34, 56, tzinfo=timezone.utc), True),
                    (datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(microseconds=1), True),
                    (datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc), False),
                    (datetime(2021, 9, 7, 12, 34, 56, tzinfo=timezone.utc), False),
                    (datetime(2999, 12, 31, 23, 59, 59, tzinfo=timezone.utc), False),
                ],
            ),

            # Boundaries and input datetimes with differing timezones
            *unpack_params(
                # Boundaries in UTC: 2021-07-01, 12:00:00 - 13:00:00
                datetime(2020, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
                datetime(2020, 7, 1, 11, 0, 0, tzinfo=timezone(timedelta(hours=-2))),
                [
                    (datetime(2020, 7, 1, 11, 59, 59, tzinfo=timezone.utc), False),  # UTC: 11:59:59
                    (datetime(2020, 7, 1, 12, 59, 59, tzinfo=timezone(timedelta(hours=1))), False),  # UTC: 11:59:59
                    (datetime(2020, 7, 1, 10, 59, 59, tzinfo=timezone(timedelta(hours=-1))), False),  # UTC: 11:59:59
                    (datetime(2020, 7, 1, 12, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 13, 0, 0, tzinfo=timezone(timedelta(hours=1))), True),  # UTC: 12:00:00
                    (datetime(2020, 7, 1, 11, 0, 0, tzinfo=timezone(timedelta(hours=-1))), True),  # UTC: 12:00:00
                    (datetime(2020, 7, 1, 13, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 14, 0, 0, tzinfo=timezone(timedelta(hours=1))), True),  # UTC: 13:00:00
                    (datetime(2020, 7, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=-1))), True),  # UTC: 13:00:00
                    (datetime(2020, 7, 1, 13, 0, 1, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 1, 14, 0, 1, tzinfo=timezone(timedelta(hours=1))), False),  # UTC: 13:00:01
                    (datetime(2020, 7, 1, 12, 0, 1, tzinfo=timezone(timedelta(hours=-1))), False),  # UTC: 13:00:01
                ],
            ),
        ],
    )
    def test_range_with_static_boundaries(lower_boundary, upper_boundary, input_datetime, expected_result):
        """ Test DateTimeRange with static datetime objects as boundaries, all datetimes having timezones. """
        dt_range = DateTimeRange(lower_boundary, upper_boundary)
        assert dt_range.contains_datetime(input_datetime) is expected_result

    @staticmethod
    def test_range_with_callable_boundaries():
        """ Test DateTimeRange with callables as boundaries. """
        # Start with boundaries [12:01:00 - 12:02:00] and narrow the boundaries by a second each iteration:
        # [12:01:01 - 12:01:59] -> [12:01:02 - 12:01:58] -> [12:01:03 - 12:02:57] -> ...
        lower_boundary = TestDatetimeCallable(datetime(2021, 1, 1, 12, 1, 0, tzinfo=timezone.utc))
        upper_boundary = TestDatetimeCallable(datetime(2021, 1, 1, 12, 2, 0, tzinfo=timezone.utc))

        # Create test DateTimeRange
        dt_range = DateTimeRange(lower_boundary, upper_boundary)

        # Define probe times as (minute, second) tuples: In each iteration, the datetime 2021-01-01 12:MM:SS will be
        # tested against the DateTimeRange
        probe_times = [(0, 59), (1, 0), (1, 1), (1, 2), (1, 58), (1, 59), (2, 0), (2, 1)]

        # Define expected results for each iteration: True means the probe datetime is contained in the DateTimeRange
        expected_result_iterations = [
            [False, True, True, True, True, True, True, False],
            [False, False, True, True, True, True, False, False],
            [False, False, False, True, True, False, False, False],
            [False, False, False, False, False, False, False, False],
        ]

        for expected_results in expected_result_iterations:
            # Iterate over all probe times combined with the expected results (e.g. ((0, 59), False) for the first run)
            for (minute, second), expected_result in zip(probe_times, expected_results):
                probe_dt = datetime(2021, 1, 1, 12, minute, second, tzinfo=timezone.utc)
                assert dt_range.contains_datetime(probe_dt) is expected_result

            # Narrow the boundaries by one second each iteration (lower boundary goes up, upper boundary goes down)
            lower_boundary.count(1)
            upper_boundary.count(-1)

    # Tests with local_timezone parameter

    @staticmethod
    @pytest.mark.parametrize(
        'lower_boundary, upper_boundary, local_timezone',
        [
            # Boundaries have explicit timezone, same as local_timezone
            (
                datetime(2010, 2, 1, 13, 0, 0, tzinfo=tz.gettz('Europe/Berlin')),  # No DST (+01:00), UTC: 12:00:00
                datetime(2010, 7, 1, 14, 0, 0, tzinfo=tz.gettz('Europe/Berlin')),  # DST (+02:00), UTC: 12:00:00
                tz.gettz('Europe/Berlin'),
            ),
            # Boundaries have explicit timezone, but different from local_timezone
            (
                datetime(2010, 2, 1, 9, 0, 0, tzinfo=timezone(timedelta(hours=-3))),  # Fixed offset, UTC: 12:00:00
                datetime(2010, 7, 1, 7, 0, 0, tzinfo=timezone(timedelta(hours=-5))),  # Fixed offset, UTC: 12:00:00
                tz.gettz('Europe/Berlin'),
            ),
            # Boundaries have no explicit timezone, local_timezone has DST
            (
                datetime(2010, 2, 1, 13, 0, 0),  # Should be interpreted as: No DST (+01:00), UTC: 12:00:00
                datetime(2010, 7, 1, 14, 0, 0),  # Should be interpreted as: DST (+02:00), UTC: 12:00:00
                tz.gettz('Europe/Berlin'),
            ),
            # Boundaries have no explicit timezone, local_timezone is UTC
            (
                datetime(2010, 2, 1, 12, 0, 0),  # Should be interpreted as UTC 12:00:00
                datetime(2010, 7, 1, 12, 0, 0),  # Should be interpreted as UTC 12:00:00
                timezone.utc,
            ),
        ],
    )
    @pytest.mark.parametrize(
        'input_datetime, expected_result',
        [
            # -- Test lower boundary

            # UTC: 11:59:59
            (datetime(2010, 2, 1, 11, 59, 59, tzinfo=timezone.utc), False),
            # UTC: 12:00:00
            (datetime(2010, 2, 1, 12, 0, 0, tzinfo=timezone.utc), True),
            # No DST, UTC: 11:59:59
            (datetime(2010, 2, 1, 12, 59, 59, tzinfo=tz.gettz('Europe/Berlin')), False),
            # No DST, UTC: 12:00:00
            (datetime(2010, 2, 1, 13, 0, 0, tzinfo=tz.gettz('Europe/Berlin')), True),
            # Fixed offset, UTC: 11:59:59
            (datetime(2010, 2, 1, 12, 59, 59, tzinfo=timezone(timedelta(hours=1))), False),
            # Fixed offset, UTC: 12:00:00
            (datetime(2010, 2, 1, 13, 0, 0, tzinfo=timezone(timedelta(hours=1))), True),
            # Fixed offset, UTC: 11:59:59
            (datetime(2010, 2, 1, 8, 59, 59, tzinfo=timezone(timedelta(hours=-3))), False),
            # Fixed offset, UTC: 12:00:00
            (datetime(2010, 2, 1, 9, 0, 0, tzinfo=timezone(timedelta(hours=-3))), True),

            # -- Test upper boundary (can be affected by Daylight Saving Time)

            # UTC: 12:00:00
            (datetime(2010, 7, 1, 12, 0, 0, tzinfo=timezone.utc), True),
            # UTC: 12:00:01
            (datetime(2010, 7, 1, 12, 0, 1, tzinfo=timezone.utc), False),
            # DST, UTC: 12:00:00
            (datetime(2010, 7, 1, 14, 0, 0, tzinfo=tz.gettz('Europe/Berlin')), True),
            # DST, UTC: 12:00:01
            (datetime(2010, 7, 1, 14, 0, 1, tzinfo=tz.gettz('Europe/Berlin')), False),
            # Fixed offset, UTC: 12:00:00
            (datetime(2010, 7, 1, 14, 0, 0, tzinfo=timezone(timedelta(hours=2))), True),
            # Fixed offset, UTC: 12:00:01
            (datetime(2010, 7, 1, 14, 0, 1, tzinfo=timezone(timedelta(hours=2))), False),
            # Fixed offset, UTC: 12:00:00
            (datetime(2010, 7, 1, 9, 0, 0, tzinfo=timezone(timedelta(hours=-3))), True),
            # Fixed offset, UTC: 12:00:01
            (datetime(2010, 7, 1, 9, 0, 1, tzinfo=timezone(timedelta(hours=-3))), False),
        ],
    )
    def test_range_with_local_timezone(
        lower_boundary,
        upper_boundary,
        local_timezone,
        input_datetime,
        expected_result,
    ):
        """ Test DateTimeRange with local_timezone parameter and boundaries with and without timezones. """
        dt_range = DateTimeRange(lower_boundary, upper_boundary)
        assert dt_range.contains_datetime(input_datetime, local_timezone=local_timezone) is expected_result

    # Test invalid parameters

    @staticmethod
    def test_lower_boundary_greater_than_upper_boundary():
        """
        Check that a ValueError is raised when a DateTime's boundaries are static datetimes and the lower boundary is
        greater than the upper boundary.
        """
        with pytest.raises(ValueError) as exception_info:
            DateTimeRange(
                lower_boundary=datetime(2021, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
                upper_boundary=datetime(2021, 7, 1, 11, 0, 0, tzinfo=timezone.utc),
            )

        assert str(exception_info.value) == 'DateTimeRange: Lower boundary cannot be greater than upper boundary.'


class DateTimeOffsetRangeTest:
    """ Tests for the DateTimeOffsetRange class. """

    @staticmethod
    @pytest.mark.parametrize(
        'pivot, offset_minus, offset_plus',
        [
            (
                None,
                timedelta(hours=1),
                None,
            ),
            (
                None,
                timedelta(hours=1),
                timedelta(days=3),
            ),
            (
                datetime(2021, 9, 8, 7, 6, 5),
                timedelta(hours=1),
                None,
            ),
            (
                datetime(2021, 9, 8, 7, 6, 5),
                None,
                timedelta(days=3),
            ),
            (
                lambda: datetime.now(),
                timedelta(hours=24),
                timedelta(hours=24),
            ),
        ],
    )
    def test_offset_range_repr(pivot, offset_minus, offset_plus):
        """ Test DateTimeOffsetRange `__repr__()` method. """
        dt_range = DateTimeOffsetRange(pivot=pivot, offset_minus=offset_minus, offset_plus=offset_plus)

        assert (
            repr(dt_range)
            == f'DateTimeOffsetRange(pivot={pivot!r}, offset_minus={offset_minus!r}, offset_plus={offset_plus!r})'
        )

    @staticmethod
    @pytest.mark.parametrize(
        'pivot, offset_minus, offset_plus, expected_dict',
        [
            # Static datetimes
            (
                datetime(2021, 9, 8, 13, 12, 0, tzinfo=timezone.utc),
                timedelta(hours=1),
                None,
                {'lower_boundary': '2021-09-08T12:12:00+00:00', 'upper_boundary': '2021-09-08T13:12:00+00:00'},
            ),
            (
                datetime(2021, 9, 8, 13, 12, 0, tzinfo=timezone.utc),
                None,
                timedelta(hours=1),
                {'lower_boundary': '2021-09-08T13:12:00+00:00', 'upper_boundary': '2021-09-08T14:12:00+00:00'},
            ),
            (
                datetime(2021, 9, 8, 13, 12, 0, tzinfo=timezone.utc),
                timedelta(minutes=10),
                timedelta(minutes=30),
                {'lower_boundary': '2021-09-08T13:02:00+00:00', 'upper_boundary': '2021-09-08T13:42:00+00:00'},
            ),

            # Callables
            (
                lambda: datetime(2021, 9, 8, 13, 12, 0),
                None,
                timedelta(hours=2),
                {'lower_boundary': '2021-09-08T13:12:00', 'upper_boundary': '2021-09-08T15:12:00'}
            ),
        ],
    )
    def test_offset_range_to_dict(pivot, offset_minus, offset_plus, expected_dict):
        """ Test DateTimeOffsetRange `to_dict()` method. """
        dt_range = DateTimeOffsetRange(pivot=pivot, offset_minus=offset_minus, offset_plus=offset_plus)
        assert dt_range.to_dict() == expected_dict

    @staticmethod
    def test_offset_range_to_dict_with_local_timezone():
        """ Test DateTimeOffsetRange `to_dict()` method with local_timezone parameter. """
        dt_range = DateTimeOffsetRange(
            pivot=datetime(2021, 9, 8, 10, 12, 0),
            offset_plus=timedelta(hours=1),
        )

        assert dt_range.to_dict(local_timezone=timezone(timedelta(hours=-3))) == {
            'lower_boundary': '2021-09-08T10:12:00-03:00',
            'upper_boundary': '2021-09-08T11:12:00-03:00',
        }

    # Tests with all datetimes having timezones

    @staticmethod
    @pytest.mark.parametrize(
        'pivot_datetime, offset_minus, offset_plus, input_datetime, expected_result',
        [
            # offset_plus only
            *unpack_params(
                datetime(2020, 7, 1, 12, 30, 0, tzinfo=timezone.utc),
                None,
                timedelta(hours=1),
                [
                    (datetime(2020, 7, 1, 12, 29, 59, 999999, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 1, 12, 30, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 13, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 13, 30, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 13, 30, 0, 1, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 2, 13, 0, 0, tzinfo=timezone.utc), False),
                ],
            ),

            # offset_minus only
            *unpack_params(
                datetime(2020, 7, 1, 12, 30, 0, tzinfo=timezone.utc),
                timedelta(minutes=30),
                None,
                [
                    (datetime(2020, 6, 30, 12, 15, 0, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 1, 11, 59, 59, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 1, 12, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 12, 30, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 12, 30, 1, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 2, 12, 15, 0, tzinfo=timezone.utc), False),
                ],
            ),

            # Both offsets set
            *unpack_params(
                datetime(2021, 7, 10, 13, 12, 0, tzinfo=timezone.utc),
                timedelta(days=1),
                timedelta(weeks=1),
                [
                    (datetime(2021, 6, 10, 13, 12, 0, tzinfo=timezone.utc), False),
                    (datetime(2021, 7, 9, 13, 11, 59, tzinfo=timezone.utc), False),
                    (datetime(2021, 7, 9, 13, 12, 0, tzinfo=timezone.utc), True),
                    (datetime(2021, 7, 10, 13, 12, 0, tzinfo=timezone.utc), True),
                    (datetime(2021, 7, 11, 13, 12, 0, tzinfo=timezone.utc), True),
                    (datetime(2021, 7, 17, 13, 12, 0, tzinfo=timezone.utc), True),
                    (datetime(2021, 7, 17, 13, 12, 1, tzinfo=timezone.utc), False),
                    (datetime(2021, 8, 10, 13, 12, 0, tzinfo=timezone.utc), False),
                ],
            ),

            # Boundaries and input datetimes with differing timezones
            *unpack_params(
                # Boundaries in UTC: 2021-07-01, 12:00:00 - 13:00:00, pivoted around 12:30:00 with different timezones
                [
                    datetime(2020, 7, 1, 12, 30, 0, tzinfo=timezone.utc),
                    datetime(2020, 7, 1, 14, 30, 0, tzinfo=timezone(timedelta(hours=2))),
                ],
                timedelta(minutes=30),
                timedelta(minutes=30),
                [
                    # UTC: 11:59:59
                    (datetime(2020, 7, 1, 11, 59, 59, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 1, 12, 59, 59, tzinfo=timezone(timedelta(hours=1))), False),

                    # UTC: 12:00:00
                    (datetime(2020, 7, 1, 12, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 11, 0, 0, tzinfo=timezone(timedelta(hours=-1))), True),

                    # UTC: 13:00:00
                    (datetime(2020, 7, 1, 13, 0, 0, tzinfo=timezone.utc), True),
                    (datetime(2020, 7, 1, 14, 0, 0, tzinfo=timezone(timedelta(hours=1))), True),

                    # UTC: 13:00:01
                    (datetime(2020, 7, 1, 13, 0, 1, tzinfo=timezone.utc), False),
                    (datetime(2020, 7, 1, 12, 0, 1, tzinfo=timezone(timedelta(hours=-1))), False),
                ],
            ),
        ],
    )
    def test_offset_range_with_static_pivot(
        pivot_datetime,
        offset_minus,
        offset_plus,
        input_datetime,
        expected_result,
    ):
        """ Test DateTimeOffsetRange with a static pivot datetime and different offsets. """
        dt_range = DateTimeOffsetRange(
            pivot=pivot_datetime,
            offset_minus=offset_minus,
            offset_plus=offset_plus,
        )

        assert dt_range.contains_datetime(input_datetime) is expected_result

    @staticmethod
    def test_offset_range_with_callable_pivot():
        """ Test DateTimeOffsetRange with a callable as pivot and different offsets. """
        # Start with 12:00:30 as pivot, counting the seconds up.
        # With the offsets of -5 seconds and +5 seconds, this results in these ranges:
        # [12:00:25 - 12:00:35] -> [12:00:26 - 12:00:36] -> [12:00:27 - 12:00:37] -> ...
        pivot_callable = TestDatetimeCallable(datetime(2021, 1, 1, 12, 0, 30, tzinfo=timezone.utc))

        # Create test object
        dt_range = DateTimeOffsetRange(
            pivot=pivot_callable,
            offset_minus=timedelta(seconds=5),
            offset_plus=timedelta(seconds=5),
        )

        # Define probe seconds: In each iteration, the datetime 2021-01-01 12:00:SS will be tested against the range
        probe_seconds = [24, 25, 26, 27, 34, 35, 36, 37, 38]

        # Define expected results for each iteration: True means the probe datetime is contained in the DateTimeRange
        expected_result_iterations = [
            [False, True, True, True, True, True, False, False, False],
            [False, False, True, True, True, True, True, False, False],
            [False, False, False, True, True, True, True, True, False],
        ]

        for expected_results in expected_result_iterations:
            # Iterate over all probe times combined with the expected results (e.g. ((0, 59), False) for the first run)
            for second, expected_result in zip(probe_seconds, expected_results):
                probe_dt = datetime(2021, 1, 1, 12, 0, second, tzinfo=timezone.utc)
                assert dt_range.contains_datetime(probe_dt) is expected_result

            # Move the pivot upwards by one second each iteration
            pivot_callable.count(1)

    @staticmethod
    def test_offset_range_with_default_pivot():
        """ Test DateTimeOffsetRange with default pivot (current time in UTC without microseconds). """
        dt_range = DateTimeOffsetRange(
            offset_minus=timedelta(seconds=5),
            offset_plus=timedelta(seconds=5),
        )

        # Test with real time and a huge buffer, I guess it is safe to assume this single test doesn't take more than
        # 4 seconds...
        now = datetime.now(tz=timezone.utc)
        assert dt_range.contains_datetime(now) is True
        assert dt_range.contains_datetime(now + timedelta(seconds=1)) is True
        assert dt_range.contains_datetime(now - timedelta(seconds=1)) is True
        assert dt_range.contains_datetime(now + timedelta(seconds=10)) is False
        assert dt_range.contains_datetime(now - timedelta(seconds=10)) is False

    # Tests with local_timezone parameter

    @staticmethod
    @pytest.mark.parametrize(
        'pivot_datetime, local_timezone',
        [
            # Pivot with explicit timezone (but different from local_timezone)
            (
                datetime(2021, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
                tz.gettz('Europe/Berlin'),
            ),

            # Pivot without timezone, local_timezone is affected by DST (UTC+2)
            (
                datetime(2021, 7, 1, 14, 0, 0),
                tz.gettz('Europe/Berlin'),
            ),

            # Pivot without timezone, local_timezone is UTC
            (
                datetime(2021, 7, 1, 12, 0, 0),
                timezone.utc,
            ),
        ],
    )
    @pytest.mark.parametrize(
        'input_datetime, expected_result',
        [
            # Input in UTC
            (datetime(2021, 7, 1, 11, 59, 59, tzinfo=timezone.utc), False),  # UTC: 11:59:59
            (datetime(2021, 7, 1, 12, 0, 0, tzinfo=timezone.utc), True),  # UTC: 12:00:00
            (datetime(2021, 7, 1, 13, 0, 0, tzinfo=timezone.utc), True),  # UTC: 13:00:00
            (datetime(2021, 7, 1, 13, 0, 1, tzinfo=timezone.utc), False),  # UTC: 13:00:01

            # Input in timezone Europe/Berlin with DST (UTC+2)
            (datetime(2021, 7, 1, 13, 59, 59, tzinfo=tz.gettz('Europe/Berlin')), False),  # UTC: 11:59:59
            (datetime(2021, 7, 1, 14, 0, 0, tzinfo=tz.gettz('Europe/Berlin')), True),  # UTC: 12:00:00
            (datetime(2021, 7, 1, 15, 0, 0, tzinfo=tz.gettz('Europe/Berlin')), True),  # UTC: 13:00:00
            (datetime(2021, 7, 1, 15, 0, 1, tzinfo=tz.gettz('Europe/Berlin')), False),  # UTC: 13:00:01

            # Input with fixed offset as timezone
            (datetime(2021, 7, 1, 8, 59, 59, tzinfo=timezone(timedelta(hours=-3))), False),  # UTC: 11:59:59
            (datetime(2021, 7, 1, 9, 0, 0, tzinfo=timezone(timedelta(hours=-3))), True),  # UTC: 12:00:00
            (datetime(2021, 7, 1, 10, 0, 0, tzinfo=timezone(timedelta(hours=-3))), True),  # UTC: 13:00:00
            (datetime(2021, 7, 1, 10, 0, 1, tzinfo=timezone(timedelta(hours=-3))), False),  # UTC: 13:00:01
        ],
    )
    def test_offset_range_with_local_timezone(pivot_datetime, local_timezone, input_datetime, expected_result):
        """ Test DateTimeOffsetRange with local_timezone parameter and different timezones or local times. """
        # Range: From pivot (12:00:00 UTC) to pivot + 1 hour (13:00:00 UTC)
        dt_range = DateTimeOffsetRange(pivot=pivot_datetime, offset_plus=timedelta(hours=1))
        assert dt_range.contains_datetime(input_datetime, local_timezone=local_timezone) is expected_result

    # Test invalid parameters

    @staticmethod
    def test_missing_offset():
        """ Check that an exception is raised when neither offset_minus nor offset_plus is specified. """
        with pytest.raises(ValueError) as exception_info:
            DateTimeOffsetRange(pivot=datetime(2021, 9, 8, 7, 6, 5, tzinfo=timezone.utc))

        assert (
            str(exception_info.value)
            == 'DateTimeOffsetRange: At least one of the parameters "offset_minus" and "offset_plus" must be specified.'
        )
