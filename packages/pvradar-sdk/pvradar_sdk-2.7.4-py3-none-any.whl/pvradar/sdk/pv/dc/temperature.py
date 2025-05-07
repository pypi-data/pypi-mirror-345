"""
Estimate the temperature of the PV module back surface ('module') or photovoltaic cells ('cell') during operation.
"""

from ...modeling.decorators import standard_resource_type
from ...modeling import R

from typing import Annotated
import pandas as pd
from pydantic import Field

from pvlib.temperature import (
    sapm_module,
    sapm_cell_from_module,
    pvsyst_cell,
)


### --- CELL TEMPERATURE --- ###


@standard_resource_type(R.cell_temperature, override_unit=True)
def pvlib_temperature_sapm_cell_from_module(
    module_temperature: Annotated[pd.Series, R.module_temperature, Field()],
    effective_poa: Annotated[pd.Series, R.effective_poa, Field()],
    sapm_temp_deltaT: float = 3,
) -> pd.Series:
    """
    Wrapper around the PVLIB implementation of the Sandia Array Performance Model (SAPM) cell temperature model.
    """
    cell_temperature = sapm_cell_from_module(
        module_temperature=module_temperature,
        poa_global=effective_poa,
        deltaT=sapm_temp_deltaT,
    )
    return cell_temperature


@standard_resource_type(R.cell_temperature, override_unit=True)
def pvlib_temperature_pvsyst_cell(
    effective_poa: Annotated[pd.Series, R.effective_poa, Field()],
    temp_air: Annotated[pd.Series, R.air_temperature, Field()],
    wind_speed: Annotated[pd.Series, R.wind_speed, Field()],
    pvsyst_temp_param_u_c: float = 29,
    pvsyst_temp_param_u_v: float = 0,
    pvsyst_temp_module_efficiency: float = 0.1,
    pvsyst_temp_alpha_absorption: float = 0.9,
) -> pd.Series:
    """
    Wrapper around the PVLIB implementation of the PVSYST cell temperature model.
    """
    cell_temperature = pvsyst_cell(
        poa_global=effective_poa,
        temp_air=temp_air,
        wind_speed=wind_speed,  # type: ignore - can be both float and pd.Series although typehint asks for float
        u_c=pvsyst_temp_param_u_c,
        u_v=pvsyst_temp_param_u_v,
        module_efficiency=pvsyst_temp_module_efficiency,
        alpha_absorption=pvsyst_temp_alpha_absorption,
    )
    return cell_temperature


### --- MODULE TEMPERATURE --- ###


@standard_resource_type(R.module_temperature, override_unit=True)
def pvlib_temperature_sapm_module(
    effective_poa: Annotated[pd.Series, R.effective_poa, Field()],
    temp_air: Annotated[pd.Series, R.air_temperature, Field()],
    wind_speed: Annotated[pd.Series, R.wind_speed, Field()],
    sapm_temp_a: float = -3.56,
    sapm_temp_b: float = -0.075,
) -> pd.Series:
    """
    Wrapper around the PVLIB implementation of the Sandia Array Performance Model (SAPM) module temperature model.
    """
    module_temperature = sapm_module(
        poa_global=effective_poa,
        temp_air=temp_air,
        wind_speed=wind_speed,
        a=sapm_temp_a,
        b=sapm_temp_b,
    )
    return module_temperature
