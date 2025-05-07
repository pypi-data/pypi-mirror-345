from datetime import tzinfo
from typing import Any, Mapping, Optional, override
import pandas as pd
from .model_context import ModelContext
from ..common.pandas_utils import interval_to_index, period_str_to_interval
from .utils import convert_by_attrs


def validate_timestamp_interval(value: pd.Interval) -> None:
    if (
        not isinstance(value, pd.Interval)
        or not isinstance(value.left, pd.Timestamp)
        or not isinstance(value.right, pd.Timestamp)
    ):
        raise ValueError('must be an Interval with pd.Timestamp endpoints')
    if value.left > value.right:
        raise ValueError('in interval the left endpoint must be less than or equal to right endpoint')


def assert_equal_timezones(
    timezone1: tzinfo | str | None, timezone2: tzinfo | str | None, complaint: str = 'timezone offsets are not equal'
):
    now = pd.Timestamp('now')
    tzinfo1 = now.tz_localize(timezone1).tzinfo
    assert tzinfo1 is not None, f'invalid timezone1 "{timezone1}"'
    tzinfo2 = now.tz_localize(timezone2).tzinfo
    assert tzinfo2 is not None, f'invalid timezone2 "{timezone2}"'
    offset1 = tzinfo1.utcoffset(now)
    offset2 = tzinfo2.utcoffset(now)
    assert offset1 == offset2, f'{complaint}: {offset1} != {offset2}'


def maybe_adjust_tz(value: pd.Interval, default_tz: Any) -> pd.Interval:
    if default_tz is None:
        return value
    if value.left.tzinfo is None:
        new_left = pd.Timestamp(value.left, tz=default_tz)
    else:
        try:
            assert_equal_timezones(value.left.tzinfo, default_tz)
            new_left = value.left
        except AssertionError:
            new_left = value.left.tz_convert(default_tz)
    if value.right.tzinfo is None:
        new_right = pd.Timestamp(value.right, tz=default_tz)
    else:
        try:
            assert_equal_timezones(value.right.tzinfo, default_tz)
            new_right = value.right
        except AssertionError:
            new_right = value.right.tz_convert(default_tz)
    return pd.Interval(new_left, new_right, closed=value.closed)


def interpret_interval(interval: Any) -> pd.Interval:
    """
    interpret incoming parameter as a interval for a context.
    Main conversions: str -> pd.Interval, closed=right -> closed=both
    """
    if isinstance(interval, (int, float)):
        if int(interval) != interval:
            raise ValueError('interval cannot be a float with a non-zero decimal part')
        if interval > 2100 or interval < 1950:
            raise ValueError(f'only years between 1950 and 2100 can be passed as interval, got {interval}')
        interval = str(int(interval))
    if isinstance(interval, str):
        interval = period_str_to_interval(interval)
    if isinstance(interval, pd.Interval) and interval.closed == 'right':
        interval = pd.Interval(interval.left, interval.right, closed='both')
    if not isinstance(interval, pd.Interval):
        raise ValueError(f'type cannot be interpreted as interval: {type(interval)}')
    return interval


def interval_to_str(interval: pd.Interval) -> str:
    return f'{interval.left.strftime("%Y-%m-%d")}..{interval.right.strftime("%Y-%m-%d")}'


class TimeSeriesModelContext(ModelContext):
    def __init__(self, *, interval: Optional[Any] = None, default_tz: Any = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._default_tz = default_tz
        if interval:
            self.interval = interval

    @property
    def default_tz(self) -> Any:
        return self._default_tz

    @default_tz.setter
    def default_tz(self, value: Any):
        self._default_tz = value
        if 'interval' in self._resources:
            self['interval'] = maybe_adjust_tz(self['interval'], value)

    @property
    def interval(self) -> pd.Interval:
        return self.resource('interval')

    @interval.setter
    def interval(self, value: Any) -> None:
        self['interval'] = value

    @override
    def on_resource_set(self, key: str, value: Any) -> Any:
        if key == 'interval':
            value = interpret_interval(value)
            validate_timestamp_interval(value)
            value = maybe_adjust_tz(value, self._default_tz)
        if key == 'default_tz':
            raise ValueError(
                'default_tz is a reserved keyword. Did you mean context.default_tz=... instead of context["default_tz"] = ...?'
            )
        return value

    def timestamps(self, freq: str = '1h') -> pd.DatetimeIndex:
        # interval = self.interval
        # if interval.left.tz is None:
        #     interval = maybe_adjust_tz(interval, self.default_tz)
        return interval_to_index(self.interval, freq)

    @override
    def _convert_by_attrs(self, value: Any, param_attrs: Mapping[str, Any]) -> Any:
        return convert_by_attrs(value, param_attrs, interval=self['interval'] if 'interval' in self else None)
