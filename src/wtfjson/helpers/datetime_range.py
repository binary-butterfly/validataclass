# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, tzinfo, timezone
from typing import Callable, Optional, Union

__all__ = [
    'BaseDateTimeRange',
    'DateTimeRange',
    'DateTimeOffsetRange',
]

# Type aliases used for type hinting
_DateTimeCallable = Callable[[], datetime]
_DateTimeBoundary = Optional[Union[datetime, _DateTimeCallable]]


class BaseDateTimeRange(ABC):
    """
    Abstract base class to implement datetime ranges (to be used with DateTimeValidator).
    """

    @abstractmethod  # pragma: nocover
    def contains_datetime(self, dt: datetime, local_timezone: Optional[tzinfo] = None) -> bool:
        """
        Abstract method to be implemented by subclasses. Should return True if a datetime is contained in the range.
        """
        raise NotImplementedError()

    @staticmethod
    def _get_datetime(boundary: _DateTimeBoundary, local_timezone: Optional[tzinfo] = None) -> Optional[datetime]:
        """
        Helper method to resolve callables to datetime objects and to apply local_timezone if necessary.
        """
        # Resolve callable to an actual datetime
        boundary_datetime = boundary() if isinstance(boundary, Callable) else boundary

        # For local datetimes, set timezone if local_timezone is given
        if boundary_datetime is not None and boundary_datetime.tzinfo is None and local_timezone is not None:
            boundary_datetime = boundary_datetime.replace(tzinfo=local_timezone)
        return boundary_datetime


class DateTimeRange(BaseDateTimeRange):
    """
    Datetime range defined by two datetimes (static or dynamic using callables), a start point and an end point. All datetimes between
    those boundary datetimes are considered inside the range. Designed for use with `DateTimeValidator`.

    It is recommended either to use only datetimes with defined timezone info (for both boundaries and input), or to specify the
    'local_datetime' parameter in the `DateTimeValidator` (or when directly calling `contains_datetime()`) if the boundary datetimes are
    not guaranteed to have timezones. Mixing datetimes with and without timezone information will result in `TypeError` exceptions!
    """

    # Boundaries (static datetimes or callables)
    lower_boundary: _DateTimeBoundary = None
    upper_boundary: _DateTimeBoundary = None

    def __init__(self, lower_boundary: _DateTimeBoundary = None, upper_boundary: _DateTimeBoundary = None):
        """
        Create a DateTimeRange with a lower and an upper boundary (both are optional and can be either static datetime objects or
        callables that return datetime objects).

        Parameters:
            lower_boundary: `datetime`, `Callable` or `None`, specifies the lower boundary (default: None)
            upper_boundary: `datetime`, `Callable` or `None`, specifies the upper boundary (default: None)
        """
        # Check validity (in case of static datetimes)
        if isinstance(lower_boundary, datetime) and isinstance(upper_boundary, datetime) and lower_boundary > upper_boundary:
            raise ValueError('DateTimeRange: Lower boundary cannot be greater than upper boundary.')

        # Save boundaries
        self.lower_boundary = lower_boundary
        self.upper_boundary = upper_boundary

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}(lower_boundary={repr(self.lower_boundary)}, upper_boundary={repr(self.upper_boundary)})'

    def contains_datetime(self, dt: datetime, local_timezone: Optional[tzinfo] = None) -> bool:
        """
        Returns True if the datetime is contained in the datetime range.

        Optionally a timezone can be specified that will be applied to the boundary datetimes if they don't have specified timezones.
        """
        lower_datetime = self._get_lower_datetime(local_timezone)
        upper_datetime = self._get_upper_datetime(local_timezone)

        # Note: These comparisons will raise TypeErrors when mixing datetimes with and without timezones
        if (lower_datetime is not None and dt < lower_datetime) or (upper_datetime is not None and dt > upper_datetime):
            return False
        return True

    def _get_lower_datetime(self, local_timezone: Optional[tzinfo] = None) -> Optional[datetime]:
        """
        Helper method to get the lower boundary as a datetime (or None), resolving callables and applying local_timezone if necessary.
        """
        return self._get_datetime(self.lower_boundary, local_timezone)

    def _get_upper_datetime(self, local_timezone: Optional[tzinfo] = None) -> Optional[datetime]:
        """
        Helper method to get the upper boundary as a datetime (or None), resolving callables and applying local_timezone if necessary.
        """
        return self._get_datetime(self.upper_boundary, local_timezone)


class DateTimeOffsetRange(BaseDateTimeRange):
    """
    Datetime range defined by a pivot datetime (static or dynamic using a callable) and one or two timedeltas as offset ('offset_minus'
    and 'offset_plus'). All datetimes between `pivot_datetime - offset_minus` and `pivot_datetime + offset_plus` are considered inside
    the range. Designed for use with `DateTimeValidator`.

    If the pivot datetime is not specified, the current time will be used as default (with tzinfo=UTC and without milli-/microseconds).

    The offset timedeltas default to 0 seconds, e.g. if you only specify 'offset_minus', the upper boundary will be the pivot datetime
    itself without offset.

    As with `DateTimeRange`, it is recommended either to use only datetimes with defined timezone info or to use the 'local_datetime'
    parameter. See `DateTimeRange` for details.
    """

    # Pivot datetime (static or callable)
    pivot: _DateTimeBoundary = None

    # Offset timedeltas
    offset_minus: timedelta = None
    offset_plus: timedelta = None

    def __init__(self, pivot: _DateTimeBoundary = None, offset_minus: timedelta = None, offset_plus: timedelta = None):
        """
        Create a DateTimeOffsetRange with a pivot datetime (static datetime or callable that returns datetime objects), and one or two
        offset. The pivot datetime defaults to the current time in UTC (dynamically generated and without milli-/microseconds).

        Parameters:
            pivot: `datetime`, `Callable` or `None`, specifies the pivot datetime (default: None, current time in UTC)
            offset_minus: `timedelta`, specifies the negative offset from the pivot (default: None, 0 seconds)
            offset_plus: `timedelta`, specifies the positive offset from the pivot (default: None, 0 seconds)
        """
        # Check parameter validity
        if offset_minus is None and offset_plus is None:
            raise ValueError('DateTimeOffsetRange: At least one of the parameters "offset_minus" and "offset_plus" must be specified.')

        # Save parameters
        self.pivot = pivot
        self.offset_minus = offset_minus if offset_minus is not None else timedelta()
        self.offset_plus = offset_plus if offset_plus is not None else timedelta()

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}(pivot={repr(self.pivot)}, offset_minus={repr(self.offset_minus)}, offset_plus={repr(self.offset_plus)})'

    def contains_datetime(self, dt: datetime, local_timezone: Optional[tzinfo] = None) -> bool:
        """
        Returns True if the datetime is contained in the datetime range.

        Optionally a timezone can be specified that will be applied to the boundary datetimes if they don't have specified timezones.
        """
        # Get pivot datetime, resolving callables if necessary
        pivot_datetime = self._get_pivot_datetime(local_timezone)

        # Calculate lower and upper boundaries
        lower_datetime = pivot_datetime - self.offset_minus
        upper_datetime = pivot_datetime + self.offset_plus

        # Note: These comparisons will raise TypeErrors when mixing datetimes with and without timezones
        if dt < lower_datetime or dt > upper_datetime:
            return False
        return True

    # Helper methods to resolve callables to datetimes and apply local_timezone

    def _get_pivot_datetime(self, local_timezone: Optional[tzinfo] = None) -> Optional[datetime]:
        """
        Helper method to get the pivot as a datetime, resolving callables and applying local_timezone if necessary, and defaulting
        to the current time in UTC.
        """
        if self.pivot is not None:
            return self._get_datetime(self.pivot, local_timezone)
        else:
            return datetime.now(timezone.utc).replace(microsecond=0)
