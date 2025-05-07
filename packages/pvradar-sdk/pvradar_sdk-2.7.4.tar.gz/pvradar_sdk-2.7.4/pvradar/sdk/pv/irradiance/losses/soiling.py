import pvlib
from typing import Annotated
import pandas as pd
from pydantic import Field
from ....modeling.decorators import standard_resource_type
from ....modeling import R
from ....common.pandas_utils import interval_to_index


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
def no_soiling_losses(
    interval: pd.Interval,
    freq: str = '1h',
) -> pd.Series:
    timestamps = interval_to_index(interval=interval, freq=freq)
    return pd.Series(0, index=timestamps)


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
def pvlib_soiling_hsu_hourly(
    *,
    pm2_5: Annotated[pd.Series, R.pm2_5_volume_concentration(to_unit='g/m^3', to_freq='h')],
    pm10: Annotated[pd.Series, R.pm10_volume_concentration(to_unit='g/m^3', to_freq='h')],
    rainfall: Annotated[pd.Series, R.rainfall(to_unit='mm', to_freq='h')],
    daily_cleaning_threshold: Annotated[float, Field(gt=0, lt=10)] = 1,
    surface_tilt_angle: Annotated[pd.Series, R.surface_tilt_angle(to_freq='h')],
    hsu_pm2_5_depo_veloc: Annotated[float, Field(gt=0)] = 0.0009,
    hsu_pm10_depo_veloc: Annotated[float, Field(gt=0)] = 0.004,
    hsu_rain_accum_period=pd.Timedelta('1d'),
) -> pd.Series:
    depo_veloc = {'2_5': hsu_pm2_5_depo_veloc, '10': hsu_pm10_depo_veloc}

    soiling_ratio = pvlib.soiling.hsu(
        rainfall=rainfall,
        cleaning_threshold=daily_cleaning_threshold,
        surface_tilt=surface_tilt_angle,
        pm2_5=pm2_5.values,
        pm10=pm10.values,
        depo_veloc=depo_veloc,
        rain_accum_period=hsu_rain_accum_period,
    )
    return 1 - soiling_ratio


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
def pvlib_soiling_hsu_daily(
    *,
    pm2_5: Annotated[pd.Series, R.pm2_5_volume_concentration(to_unit='g/m^3', to_freq='D')],
    pm10: Annotated[pd.Series, R.pm10_volume_concentration(to_unit='g/m^3', to_freq='D')],
    rainfall: Annotated[pd.Series, R.rainfall(to_unit='mm', to_freq='D')],
    daily_cleaning_threshold: Annotated[float, Field(gt=0, lt=10)] = 1,
    surface_tilt_angle: Annotated[pd.Series, R.surface_tilt_angle(to_freq='D')],
    hsu_pm2_5_depo_veloc: Annotated[float, Field(gt=0)] = 0.0009,
    hsu_pm10_depo_veloc: Annotated[float, Field(gt=0)] = 0.004,
    hsu_rain_accum_period=pd.Timedelta('1d'),
) -> pd.Series:
    depo_veloc = {'2_5': hsu_pm2_5_depo_veloc, '10': hsu_pm10_depo_veloc}

    soiling_ratio = pvlib.soiling.hsu(
        rainfall=rainfall,
        cleaning_threshold=daily_cleaning_threshold,
        surface_tilt=surface_tilt_angle,
        pm2_5=pm2_5,
        pm10=pm10,
        depo_veloc=depo_veloc,
        rain_accum_period=hsu_rain_accum_period,
    )
    return 1 - soiling_ratio


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
def pvlib_soiling_kimber(
    *,
    rainfall: Annotated[pd.Series, R.rainfall(to_unit='mm')],
    kimber_cleaning_threshold: int = 6,
    kimber_soiling_loss_rate: float = 0.0015,
    kimber_grace_period: int = 14,
    kimber_max_soiling: float = 0.3,
    kimber_initial_soiling: int = 0,
    kimber_rain_accum_hours: int = 24,
) -> pd.Series:
    soiling_loss_factor = pvlib.soiling.kimber(
        rainfall=rainfall,
        cleaning_threshold=kimber_cleaning_threshold,
        soiling_loss_rate=kimber_soiling_loss_rate,
        grace_period=kimber_grace_period,
        max_soiling=kimber_max_soiling,
        initial_soiling=kimber_initial_soiling,
        rain_accum_period=kimber_rain_accum_hours,
    )

    return soiling_loss_factor
