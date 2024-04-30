"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Callable, Dict, Optional, Tuple, Union

__all__ = [
    'BaseDateTimeRange',
    'DateTimeRange',
    'DateTimeOffsetRange',
]

# Type aliases used for type hinting
_DateTimeCallable = Callable[[], datetime]
_DateTimeBoundary = Union[datetime, _DateTimeCallable]


class BaseDateTimeRange(ABC):
    """
    Abstract base class to implement datetime ranges (to be used with `DateTimeValidator`).
    """

    @abstractmethod
    def contains_datetime(self, dt: datetime, local_timezone: Optional[tzinfo] = None) -> bool:
        """
        Abstract method to be implemented by subclasses. Should return `True` if a datetime is contained in the range.
        """
        raise NotImplementedError()

    @abstractmethod
    def to_dict(self, local_timezone: Optional[tzinfo] = None) -> Dict[str, str]:
        """
        Abstract method to be implemented by subclasses. Should return a dictionary with string representations of the
        range boundaries, suitable for the `DateTimeRangeError` exception to generate JSON error responses.
        """
        raise NotImplementedError()

    # Helper methods

    @staticmethod
    def _resolve_datetime_boundary(
        boundary: _DateTimeBoundary,
        local_timezone: Optional[tzinfo] = None,
    ) -> datetime:
        """
        Helper method to resolve callables to datetime objects and to apply `local_timezone` if necessary.
        """
        # Resolve callable to an actual datetime
        boundary_datetime = boundary() if callable(boundary) else boundary

        # For local datetimes, set timezone if local_timezone is given
        if boundary_datetime.tzinfo is None and local_timezone is not None:
            boundary_datetime = boundary_datetime.replace(tzinfo=local_timezone)

        return boundary_datetime


class DateTimeRange(BaseDateTimeRange):
    """
    Datetime range defined by two datetimes (static or dynamic using callables), a start point and an end point.

    All datetimes between those boundary datetimes are considered inside the range. Designed for use with
    `DateTimeValidator`.

    It is recommended either to use only datetimes with defined timezone info (for both boundaries and input), or to
    specify the `local_datetime` parameter in the `DateTimeValidator` (or when directly calling `contains_datetime()`)
    if the boundary datetimes are not guaranteed to have timezones. Mixing datetimes with and without timezone
    information will result in `TypeError` exceptions!
    """

    # Boundaries (static datetimes or callables)
    lower_boundary: Optional[_DateTimeBoundary] = None
    upper_boundary: Optional[_DateTimeBoundary] = None

    def __init__(
        self,
        lower_boundary: Optional[_DateTimeBoundary] = None,
        upper_boundary: Optional[_DateTimeBoundary] = None,
    ):
        """
        Creates a `DateTimeRange` with a lower and an upper boundary (both are optional and can be either static
        `datetime` objects or callables that return `datetime` objects).

        Parameters:
            `lower_boundary`: `datetime`, `Callable` or `None`, specifies the lower boundary (default: `None`)
            `upper_boundary`: `datetime`, `Callable` or `None`, specifies the upper boundary (default: `None`)
        """
        # Check validity (in case of static datetimes)
        if (
            isinstance(lower_boundary, datetime) and isinstance(upper_boundary, datetime)
            and lower_boundary > upper_boundary
        ):
            raise ValueError('DateTimeRange: Lower boundary cannot be greater than upper boundary.')

        # Save boundaries
        self.lower_boundary = lower_boundary
        self.upper_boundary = upper_boundary

    def __repr__(self) -> str:
        return f'{type(self).__name__}(lower_boundary={self.lower_boundary!r}, upper_boundary={self.upper_boundary!r})'

    def contains_datetime(self, dt: datetime, local_timezone: Optional[tzinfo] = None) -> bool:
        """
        Returns `True` if the datetime is contained in the datetime range.

        Optionally a timezone can be specified that will be applied to the boundary datetimes if they don't have
        specified timezones.
        """
        lower_datetime = self._get_lower_datetime(local_timezone)
        upper_datetime = self._get_upper_datetime(local_timezone)

        # Note: These comparisons will raise TypeErrors when mixing datetimes with and without timezones
        return (lower_datetime is None or dt >= lower_datetime) and (upper_datetime is None or dt <= upper_datetime)

    def to_dict(self, local_timezone: Optional[tzinfo] = None) -> Dict[str, str]:
        """
        Returns a dictionary with string representations of the range boundaries, suitable for the `DateTimeRangeError`
        exception to generate JSON error responses.
        """
        lower_datetime = self._get_lower_datetime(local_timezone)
        upper_datetime = self._get_upper_datetime(local_timezone)

        return {
            **({'lower_boundary': lower_datetime.isoformat()} if lower_datetime is not None else {}),
            **({'upper_boundary': upper_datetime.isoformat()} if upper_datetime is not None else {}),
        }

    def _get_lower_datetime(self, local_timezone: Optional[tzinfo] = None) -> Optional[datetime]:
        """
        Helper method to get the lower boundary as a `datetime` (or `None`), resolving callables and applying
        `local_timezone` if necessary.
        """
        if self.lower_boundary is None:
            return None
        else:
            return self._resolve_datetime_boundary(self.lower_boundary, local_timezone)

    def _get_upper_datetime(self, local_timezone: Optional[tzinfo] = None) -> Optional[datetime]:
        """
        Helper method to get the upper boundary as a `datetime` (or `None`), resolving callables and applying
        `local_timezone` if necessary.
        """
        if self.upper_boundary is None:
            return None
        else:
            return self._resolve_datetime_boundary(self.upper_boundary, local_timezone)


class DateTimeOffsetRange(BaseDateTimeRange):
    """
    Datetime range defined by a pivot datetime (static or dynamic using a callable) and one or two timedeltas as offset
    (`offset_minus` and `offset_plus`).

    All datetimes between `pivot_datetime - offset_minus` and `pivot_datetime + offset_plus` are considered inside the
    range. Designed for use with `DateTimeValidator`.

    If the pivot datetime is not specified, the current time will be used as default (with `tzinfo=UTC` and without
    milli-/microseconds).

    The offset timedeltas default to 0 seconds, e.g. if you only specify `offset_minus`, the upper boundary will be the
    pivot datetime itself without offset.

    As with `DateTimeRange`, it is recommended either to use only datetimes with defined timezone information or to use
    the `local_datetime` parameter. See `DateTimeRange` for details.
    """

    # Pivot datetime (static or callable)
    pivot: Optional[_DateTimeBoundary] = None

    # Offset timedeltas
    offset_minus: Optional[timedelta] = None
    offset_plus: Optional[timedelta] = None

    def __init__(
        self,
        pivot: Optional[_DateTimeBoundary] = None,
        offset_minus: Optional[timedelta] = None,
        offset_plus: Optional[timedelta] = None,
    ):
        """
        Creates a `DateTimeOffsetRange` with a pivot datetime (static `datetime` or callable that returns `datetime`
        objects), and one or two offset. The pivot datetime defaults to the current time in UTC (dynamically generated
        and without milli-/microseconds).

        Parameters:
            `pivot`: `datetime`, `Callable` or `None`, specifies the pivot datetime (default: `None`, current UTC time)
            `offset_minus`: `timedelta`, specifies the negative offset from the pivot (default: `None`, 0 seconds)
            `offset_plus`: `timedelta`, specifies the positive offset from the pivot (default: `None`, 0 seconds)
        """
        # Check parameter validity
        if offset_minus is None and offset_plus is None:
            raise ValueError(
                'DateTimeOffsetRange: At least one of the parameters "offset_minus" and "offset_plus" must be '
                'specified.'
            )

        # Save parameters
        self.pivot = pivot
        self.offset_minus = offset_minus
        self.offset_plus = offset_plus

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}(pivot={self.pivot!r}, offset_minus={self.offset_minus!r}, '
            f'offset_plus={self.offset_plus!r})'
        )

    def contains_datetime(self, dt: datetime, local_timezone: Optional[tzinfo] = None) -> bool:
        """
        Returns `True` if the datetime is contained in the datetime range.

        Optionally a timezone can be specified that will be applied to the boundary datetimes if they don't have
        specified timezones.
        """
        # Calculate lower and upper boundaries
        lower_datetime, upper_datetime = self._get_boundaries(local_timezone)

        # Note: These comparisons will raise TypeErrors when mixing datetimes with and without timezones
        return lower_datetime <= dt <= upper_datetime

    def to_dict(self, local_timezone: Optional[tzinfo] = None) -> Dict[str, str]:
        """
        Returns a dictionary with string representations of the range boundaries (calculating `lower_datetime` and
        `upper_datetime` from the pivot minus/plus the offsets), suitable for the `DateTimeRangeError` exception to
        generate JSON error responses.
        """
        # Calculate lower and upper boundaries
        lower_datetime, upper_datetime = self._get_boundaries(local_timezone)

        return {
            'lower_boundary': lower_datetime.isoformat(),
            'upper_boundary': upper_datetime.isoformat(),
        }

    # Helper methods to resolve callables to datetimes and apply local_timezone

    def _get_pivot_datetime(self, local_timezone: Optional[tzinfo] = None) -> datetime:
        """
        Helper method to get the pivot as a datetime, resolving callables and applying `local_timezone` if necessary,
        and defaulting to the current time in UTC.
        """
        if self.pivot is None:
            return datetime.now(timezone.utc).replace(microsecond=0)
        else:
            return self._resolve_datetime_boundary(self.pivot, local_timezone)

    def _get_boundaries(self, local_timezone: Optional[tzinfo] = None) -> Tuple[datetime, datetime]:
        """
        Helper method to get the lower and upper boundaries as datetimes, resolving callables and applying
        `local_timezone` if necessary.
        """
        # Get pivot datetime, resolving callables if necessary
        pivot_datetime = self._get_pivot_datetime(local_timezone)

        # Calculate lower and upper boundaries
        lower_datetime = pivot_datetime - self.offset_minus if self.offset_minus is not None else pivot_datetime
        upper_datetime = pivot_datetime + self.offset_plus if self.offset_plus is not None else pivot_datetime
        return lower_datetime, upper_datetime
