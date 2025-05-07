import pvlib
from typing import Annotated
import pandas as pd
from ....modeling.decorators import standard_resource_type
from ....modeling import R


@standard_resource_type(R.reflection_loss_factor, override_unit=True)
def pvlib_iam_physical(
    aoi: Annotated[pd.Series, R.angle_of_incidence],
    physical_iam_n: float = 1.526,  # effective index of refraction (unitless)
    physical_iam_K: float = 4,  # glazing extinction coefficient in units of 1/meters
    physical_iam_L: float = 0.002,  #  glazing thickness in units of meters
    physical_iam_n_ar: float
    | None = None,  # The effective index of refraction of the anti-reflective (AR) coating (unitless). If n_ar is not supplied, no AR coating is applied. A typical value for the effective index of an AR coating is 1.29.
):
    """
    Wrapper around the PVLIB implementation of the "Physical IAM model".
    https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.iam.physical.html
    """
    iam = pvlib.iam.physical(
        aoi=aoi,
        n=physical_iam_n,
        K=physical_iam_K,
        L=physical_iam_L,
        n_ar=physical_iam_n_ar,
    )

    return 1 - iam
