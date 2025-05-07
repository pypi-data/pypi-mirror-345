from typing import Annotated
import pvlib
import pandas as pd
import pvlib.transformer

from ...pv.design import PvradarSiteDesign
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_to_resource


@standard_resource_type(R.ac_power, override_unit=True)
def pvlib_transformer_simple_efficiency(
    inverter_power: Annotated[pd.Series, R.inverter_power],
    design: PvradarSiteDesign,
) -> pd.Series:
    transformer = design.transformer
    ac_power = pvlib.transformer.simple_efficiency(
        input_power=inverter_power,
        no_load_loss=transformer.no_load_loss,
        load_loss=transformer.full_load_loss,
        transformer_rating=design.array.rated_ac_power,  # match inverter rating
    )
    return ac_power


@standard_resource_type(R.ac_energy, override_unit=True)
def pvradar_ac_energy_from_power(
    ac_power: Annotated[pd.Series, R.ac_power(to_unit='W')],
):
    return convert_to_resource(
        ac_power,
        R.ac_energy(to_freq='h', set_unit='Wh'),
    )
