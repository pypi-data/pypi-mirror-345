import pvlib
from typing import Annotated
import pandas as pd
import numpy as np
from pydantic import Field

from ....modeling.decorators import standard_resource_type
from ....modeling import R, resample_series
from ....common.pandas_utils import interval_to_index
from ...design import ArrayDesign, FixedStructureDesign


@standard_resource_type(R.snow_loss_factor, override_unit=True)
def no_snow_losses(
    interval: pd.Interval,
    freq: str = '1h',
) -> pd.Series:
    timestamps = interval_to_index(interval=interval, freq=freq)
    return pd.Series(0, index=timestamps)


@standard_resource_type(R.snow_coverage, override_unit=True)
def pvlib_snow_coverage_marion(
    snowfall: Annotated[pd.Series, R.snowfall(to_freq='h', to_unit='cm'), Field()],
    poa_irradiance: Annotated[pd.Series, R.global_poa_on_front(to_freq='h', to_unit='W/m^2'), Field()],
    air_temperature: Annotated[pd.Series, R.air_temperature(to_freq='h', to_unit='degC'), Field()],
    array: Annotated[ArrayDesign, Field()],
    marion_snowfall_threshold: Annotated[float, Field(ge=0)] = 1,
    marion_can_slide_coefficient: Annotated[float, Field(le=0)] = -80.0,
    marion_slide_amount_coefficient: Annotated[float, Field(ge=0)] = 0.197,
    marion_initial_coverage: Annotated[float, Field(ge=0, le=1)] = 0,
) -> pd.Series:
    # Calculate coverage factor
    snow_coverage = pvlib.snow.coverage_nrel(
        snowfall=snowfall,
        poa_irradiance=poa_irradiance,
        temp_air=air_temperature,
        surface_tilt=get_max_tilt_angle(array.structure),
        initial_coverage=marion_initial_coverage,  # type: ignore
        threshold_snowfall=marion_snowfall_threshold,
        can_slide_coefficient=marion_can_slide_coefficient,
        slide_amount_coefficient=marion_slide_amount_coefficient,
    )

    # inherit freq, so that there is no guessing in the downstream
    if poa_irradiance.attrs.get('freq'):
        snow_coverage.attrs['freq'] = poa_irradiance.attrs['freq']

    return snow_coverage


@standard_resource_type(R.snow_loss_factor, override_unit=True)
def pvlib_snow_loss_marion(
    snow_coverage: Annotated[pd.Series, R.snow_coverage],
    array: ArrayDesign,
) -> pd.Series:
    if array.module_orientation == 'horizontal':
        num_cell_strings = array.module.cell_string_count * array.number_modules_cross_section
    else:
        if array.module.half_cell:
            # half cell: module separated in two parts along long side
            num_cell_strings = array.number_modules_cross_section * 2
        else:
            num_cell_strings = array.number_modules_cross_section

    snow_loss_factor = np.ceil(snow_coverage * num_cell_strings) / num_cell_strings

    # let's keep type checking happy
    assert isinstance(snow_loss_factor, pd.Series)

    if snow_coverage.attrs.get('freq'):
        snow_loss_factor.attrs['freq'] = snow_coverage.attrs['freq']

    return snow_loss_factor


@standard_resource_type(R.snow_loss_factor, override_unit=True)
def pvlib_snow_loss_townsend(
    snowfall: Annotated[pd.Series, R.snowfall(to_freq='D', to_unit='cm'), Field()],
    poa_irradiance_hourly: Annotated[pd.Series, R.global_poa_on_front(to_freq='h', to_unit='W/m^2'), Field()],
    air_temperature: Annotated[pd.Series, R.air_temperature(to_freq='MS', to_unit='degC'), Field()],
    relative_humidity: Annotated[pd.Series, R.relative_humidity(to_freq='MS', to_unit='%'), Field()],
    array: ArrayDesign,
    townsend_angle_of_repose: Annotated[float, Field(ge=0, le=90)] = 40,  # in deg
    townsend_snow_event_threshold: Annotated[float, Field(ge=0)] = 1.27,  # 0.5 in/day in cm/day
    townsend_string_factor: Annotated[float, Field(ge=0)] = 0.75,
    # should be 0.75 if more than one module in cross-section, and 1.0 otherwise
) -> pd.Series:
    # counting how often the snow threshold was surpassed = snow event
    snow_events = snowfall > townsend_snow_event_threshold
    snow_events_monthly = snow_events.resample('MS').sum()
    snowfall_monthly = snowfall.resample('MS').sum()

    # integrate irradiance to irradiation
    monthly_irradiation = resample_series(poa_irradiance_hourly, freq='MS', agg='sum')

    # running pvlib model
    dc_loss_townsend = pvlib.snow.loss_townsend(
        snow_total=snowfall_monthly,
        snow_events=snow_events_monthly,
        surface_tilt=get_max_tilt_angle(array.structure),
        relative_humidity=relative_humidity,
        temp_air=air_temperature,
        poa_global=monthly_irradiation,
        slant_height=array.collector_width,
        lower_edge_height=array.module_clearance,
        string_factor=townsend_string_factor,
        angle_of_repose=townsend_angle_of_repose,  # type: ignore
    )

    return dc_loss_townsend


def get_max_tilt_angle(structure) -> float:
    """The maximum tilt angle of the structure / module."""
    if isinstance(structure, FixedStructureDesign):
        return structure.tilt
    else:
        return structure.max_tracking_angle
