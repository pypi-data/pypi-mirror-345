"""
Estimate the inverter power output.
"""

from typing import Annotated
import pvlib
import pandas as pd
from ...pv.design import ArrayDesign
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_to_resource


@standard_resource_type(R.inverter_power, override_unit=True)
def pvlib_inverter_pvwatts(
    dc_power: Annotated[pd.Series, R.dc_power],
    array: ArrayDesign,
    reference_inverter_efficiency: float = 0.9637,
) -> pd.Series:
    """
    This simplified model describes all inverters as one big inverter connected to the all dc modules.
    """
    inverter = array.inverter
    inverter_power = pvlib.inverter.pvwatts(
        pdc=dc_power,
        pdc0=array.rated_ac_power,
        eta_inv_nom=inverter.nominal_efficiency,
        eta_inv_ref=reference_inverter_efficiency,
    )
    return inverter_power


@standard_resource_type(R.inverter_energy, override_unit=True)
def pvradar_inverter_energy_from_power(
    inverter_power: Annotated[pd.Series, R.inverter_power(to_unit='W')],
):
    return convert_to_resource(
        inverter_power,
        R.inverter_energy(to_freq='h', set_unit='Wh'),
    )
