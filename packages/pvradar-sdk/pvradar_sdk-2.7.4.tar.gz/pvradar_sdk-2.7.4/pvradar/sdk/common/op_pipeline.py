from io import StringIO
from typing import Any, Callable, Optional, Self, TypedDict, Literal, NotRequired

import numpy as np
import pandas as pd

from ..modeling.basics import Attrs


class OpPipelineExecutor:
    def __init__(self) -> None:
        self.ops: dict[str, Callable] = {}

    def register_op(self, op: Callable | list[Callable], name: Optional[str] = None) -> Self:
        if isinstance(op, list):
            for one_op in op:
                self.register_op(one_op)
        else:
            if name is None:
                if hasattr(op, 'name'):
                    name = getattr(op, 'name')
                else:
                    name = op.__name__
            assert name is not None
            self.ops[name] = op
        return self

    def execute(self, *, ops: list[Any], value: Optional[Any] = None) -> Any:
        for op_recipe in ops:
            op_name = op_recipe['op']
            if op_name not in self.ops:
                raise ValueError(f'op {op_name} not registered')
            value = self.ops[op_name](op_recipe, value)
        return value


class OpRecipe(TypedDict):
    op: str


class JsonValueOpRecipe(OpRecipe):
    value: int | float | str | dict


def json_value(op_recipe: JsonValueOpRecipe, value: Any = None) -> Any:
    value = op_recipe['value']
    assert isinstance(value, (int, float, str, dict))
    return op_recipe['value']


class JsonToDataFrameOpRecipe(OpRecipe):
    datetime_column: str | None
    datetime_format: NotRequired[Attrs]


class CsvToDataFrameOpRecipe(JsonToDataFrameOpRecipe):
    delimiter: NotRequired[Attrs]
    decimal: NotRequired[Attrs]


def index_dataframe(op_recipe: JsonToDataFrameOpRecipe, value: pd.DataFrame) -> pd.DataFrame:
    assert 'datetime_column' in op_recipe  # can be None, but must be defined
    datetime_column = op_recipe.get('datetime_column')
    assert datetime_column is None or isinstance(datetime_column, str)
    datetime_format = op_recipe.get('datetime_format')
    assert datetime_format is None or isinstance(datetime_format, str)
    assert isinstance(value, pd.DataFrame)
    if datetime_column is not None:
        if datetime_format is None:
            assert not value[datetime_column].str.contains(r'\d+/\d+/\d+').any(), 'datetime_format must be defined'
        value[datetime_column] = pd.to_datetime(value[datetime_column], format=datetime_format)
        value.set_index(datetime_column, inplace=True)
    return value


def csv_to_dataframe(op_recipe: CsvToDataFrameOpRecipe, value: str) -> pd.DataFrame:
    delimiter = op_recipe.get('delimiter', ',')
    assert isinstance(delimiter, str)
    decimal = op_recipe.get('decimal', '.')
    assert isinstance(decimal, str)
    assert isinstance(value, str)
    return index_dataframe(op_recipe, pd.read_csv(StringIO(value), delimiter=delimiter, decimal=decimal))


class CsvToSeriesOpRecipe(CsvToDataFrameOpRecipe):
    column: str | int


def csv_to_series(op_recipe: CsvToSeriesOpRecipe, value: str) -> pd.Series:
    assert 'column' in op_recipe
    column = op_recipe['column']
    assert isinstance(column, (str, int))
    return csv_to_dataframe(op_recipe, value)[column]


class JsonToSeriesOpRecipe(JsonToDataFrameOpRecipe):
    column: str


def json_to_dataframe(op_recipe: JsonToDataFrameOpRecipe, value: dict) -> pd.DataFrame:
    assert isinstance(value, dict)
    return index_dataframe(op_recipe, pd.DataFrame(value['rows']))


def json_to_series(op_recipe: JsonToSeriesOpRecipe, value: dict) -> pd.Series:
    assert 'column' in op_recipe
    column = op_recipe['column']
    assert isinstance(column, str)
    return json_to_dataframe(op_recipe, value)[column]


class AggregateOpRecipe(OpRecipe):
    freq: str
    agg: Literal['sum', 'mean', 'min', 'max']
    weight_column: NotRequired[str]
    # weight_resource: NotRequired[Attrs]


def aggregate(op_recipe: AggregateOpRecipe, value: pd.DataFrame | pd.Series) -> pd.Series | pd.DataFrame:
    freq = op_recipe['freq']
    assert isinstance(freq, str)
    agg = op_recipe['agg']
    assert isinstance(agg, str)
    weight_column = op_recipe.get('weight_column')
    assert weight_column is None or isinstance(weight_column, str)
    assert isinstance(value, (pd.DataFrame, pd.Series))
    # weight_resource = op_recipe.get('weight_resource')
    # assert weight_resource is None or isinstance(weight_resource, dict)
    if weight_column is not None:
        value = value.mul(value[weight_column] / value[weight_column].sum(), axis=0)
    if isinstance(value, pd.DataFrame):
        return value.groupby(pd.Grouper(freq=freq)).agg(agg)
    return value.resample(freq).agg(agg)


class AddOpRecipe(OpRecipe):
    value: int | float


def add(op_recipe: AddOpRecipe, value: pd.DataFrame | pd.Series) -> Any:
    adder = op_recipe.get('value')
    assert isinstance(adder, (int, float))
    assert isinstance(value, (pd.DataFrame, pd.Series))
    return value + adder


class MultiplyOpRecipe(OpRecipe):
    value: int | float


def multiply(op_recipe: MultiplyOpRecipe, value: pd.DataFrame | pd.Series) -> Any:
    multiplier = op_recipe.get('value')
    assert isinstance(multiplier, (int, float))
    assert isinstance(value, (pd.DataFrame, pd.Series))
    return value * multiplier


class ReindexOpRecipe(OpRecipe):
    freq: str
    start_datetime: NotRequired[str]
    end_datetime: NotRequired[str]


def reindex(op_recipe: ReindexOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    freq = op_recipe.get('freq')
    assert isinstance(freq, str)
    start_datetime = op_recipe.get('start_datetime')
    assert start_datetime is None or isinstance(start_datetime, str)
    end_datetime = op_recipe.get('end_datetime')
    assert end_datetime is None or isinstance(end_datetime, str)
    assert isinstance(value, (pd.DataFrame, pd.Series))
    min_datetime = value.index.min()
    max_datetime = value.index.max()
    assert isinstance(min_datetime, pd.Timestamp) and isinstance(max_datetime, pd.Timestamp)
    index_start = min_datetime if start_datetime is None else pd.to_datetime(start_datetime)
    index_end = max_datetime if end_datetime is None else pd.to_datetime(end_datetime)
    return value.reindex(pd.date_range(start=index_start, end=index_end, freq=freq))


class LimitOpRecipe(OpRecipe):
    min: NotRequired[float | int]
    max: NotRequired[float | int]


def limit(op_recipe: LimitOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    min_value = op_recipe.get('min')
    assert min_value is None or isinstance(min_value, (float, int))
    max_value = op_recipe.get('max')
    assert max_value is None or isinstance(max_value, (float, int))
    assert min_value is not None or max_value is not None
    assert isinstance(value, (pd.DataFrame, pd.Series))
    if min_value is not None:
        value = value.where(value >= min_value, min_value)  # type: ignore
    if max_value is not None:
        value = value.where(value <= max_value, max_value)  # type: ignore
    return value


class CutOffOpRecipe(OpRecipe):
    min: NotRequired[float | int]
    max: NotRequired[float | int]


def cut_off(op_recipe: CutOffOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    min_value = op_recipe.get('min')
    assert min_value is None or isinstance(min_value, (float, int))
    max_value = op_recipe.get('max')
    assert max_value is None or isinstance(max_value, (float, int))
    assert isinstance(value, (pd.DataFrame, pd.Series))
    if min_value is not None:
        value = value.where(value >= min_value, np.nan)  # type: ignore
    if max_value is not None:
        value = value.where(value <= max_value, np.nan)  # type: ignore
    return value


class ExcludeOpRecipe(OpRecipe):
    min: NotRequired[str | float | int]
    max: NotRequired[str | float | int]


def exclude(op_recipe: ExcludeOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    min_index = op_recipe.get('min')
    assert min_index is None or isinstance(min_index, (str, float, int))
    max_index = op_recipe.get('max')
    assert max_index is None or isinstance(max_index, (str, float, int))
    assert min_index is not None or max_index is not None
    assert isinstance(min_index, str) == isinstance(max_index, str), 'must be both `str` or both `float | int`'
    if isinstance(min_index, str):
        min_index = pd.to_datetime(min_index)
    if isinstance(max_index, str):
        max_index = pd.to_datetime(max_index)
    assert isinstance(value, (pd.DataFrame, pd.Series))
    condition = False
    if min_index is not None:
        condition |= value.index.to_series() < min_index
    if max_index is not None:
        condition |= value.index.to_series() > max_index
    return value.where(condition, np.nan)  # type: ignore


class FillOpRecipe(OpRecipe):
    value: NotRequired[float | int]
    method: NotRequired[Literal['ffill', 'bfill', 'interpolate']]


def fill(op_recipe: FillOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    fill_value = op_recipe.get('value')
    assert fill_value is None or isinstance(fill_value, (float, int))
    method = op_recipe.get('method')
    assert method is None or isinstance(method, str)
    assert fill_value is None or method is None  # cannot co-exist
    assert isinstance(value, (pd.DataFrame, pd.Series))
    if fill_value is not None:
        return value.fillna(fill_value)
    if method is not None:
        return getattr(value, method)()
    raise AssertionError('`value` or `method` must be defined')


class PickOpRecipe(OpRecipe):
    columns: list[str]


def pick(op_recipe: PickOpRecipe, value: pd.DataFrame) -> pd.DataFrame:
    columns = op_recipe.get('columns')
    assert isinstance(columns, list)
    assert isinstance(value, pd.DataFrame)
    return value[columns]


class AssertNoGapsOpRecipe(OpRecipe):
    freq: str


def assert_no_gaps(op_recipe: AssertNoGapsOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    freq = op_recipe.get('freq')
    assert isinstance(freq, str)
    assert isinstance(value, (pd.DataFrame, pd.Series))
    expected_index = pd.date_range(start=value.index.min(), end=value.index.max(), freq=freq)
    assert len(expected_index) >= len(value), 'more records than expected'
    if len(expected_index) > len(value):
        unexpected = expected_index.difference(value.index)
        assert all(unexpected.day_of_year == 60)  # 29th Feb
    return value


class AssertFullYearsOpRecipe(OpRecipe):
    freq: str


def assert_full_years(op_recipe: AssertFullYearsOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    freq = op_recipe.get('freq')
    assert isinstance(freq, str)
    assert isinstance(value, (pd.DataFrame, pd.Series))
    assert isinstance(value.index, pd.DatetimeIndex), 'op assert_full_years expects DatetimeIndex'
    years = value.index.year.unique()
    for year in years:
        year_records = value[value.index.year == year]
        min_record = year_records.index.min()
        max_record = year_records.index.max()
        pre_min_date_range = pd.date_range(start=f'{year}-01-01', end=min_record, freq=freq)
        assert len(pre_min_date_range) == 1, f'min_record for the "{year}" is not the first record of the year'
        post_max_date_range = pd.date_range(start=max_record, end=f'{year + 1}-01-01', freq=freq, inclusive='left')
        assert len(post_max_date_range) == 1, f'max_record for the "{year}" is not the last record of the year'
        assert_no_gaps({'op': 'assert_no_gaps', 'freq': freq}, year_records)
    return value


class AssertNoEmptyOpRecipe(OpRecipe):
    pass


def assert_no_empty(op_recipe: AssertNoEmptyOpRecipe, value: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    assert isinstance(value, (pd.DataFrame, pd.Series))
    assert not value.isna().any().any()  # type: ignore # double `any` for DataFrame
    return value


class StdExecutor(OpPipelineExecutor):
    def __init__(self) -> None:
        super().__init__()
        self.register_op(
            [
                # -------- input
                json_value,
                # --------------------------------
                # -------- type transformation
                csv_to_dataframe,
                csv_to_series,
                json_to_dataframe,
                json_to_series,
                # --------------------------------
                # -------- data processing
                aggregate,
                add,
                multiply,
                reindex,
                limit,
                cut_off,
                exclude,
                fill,
                pick,
                # --------------------------------
                # -------- assertions
                assert_no_gaps,
                assert_full_years,
                assert_no_empty,
            ]
        )
