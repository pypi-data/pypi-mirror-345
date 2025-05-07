"""
Estimate the output of a PV module at Maximum-Power-Point (MPP) conditions.
"""

from typing import Annotated
import pvlib
import pandas as pd
from ...pv.design import ArrayDesign
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_to_resource


@standard_resource_type(R.dc_power, override_unit=True)
def pvlib_pvsystesm_pvwatts_dc(
    effective_poa: Annotated[pd.Series, R.effective_poa],
    cell_temperature: Annotated[pd.Series, R.cell_temperature],
    array: ArrayDesign,
    reference_temperature=25.0,
) -> pd.Series:
    module = array.module
    power_one_module = pvlib.pvsystem.pvwatts_dc(
        g_poa_effective=effective_poa,
        temp_cell=cell_temperature,
        pdc0=module.rated_power,
        gamma_pdc=module.temperature_coefficient_power,
        temp_ref=reference_temperature,
    )
    dc_power = power_one_module / module.rated_power * array.rated_dc_power
    return dc_power


@standard_resource_type(R.dc_energy, override_unit=True)
def pvradar_dc_energy_from_power(
    dc_power: Annotated[pd.Series, R.dc_power(to_unit='W')],
):
    return convert_to_resource(
        dc_power,
        R.dc_energy(to_freq='h', set_unit='Wh'),
    )
