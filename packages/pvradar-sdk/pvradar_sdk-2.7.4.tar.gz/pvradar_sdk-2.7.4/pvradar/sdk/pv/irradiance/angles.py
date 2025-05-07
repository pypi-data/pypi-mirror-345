from typing import Annotated
from ...common.pandas_utils import interval_to_index
from ...modeling.model_context import ModelContext
from pvlib.location import Location
from ...modeling.decorators import standard_resource_type
from ...modeling import R
import pandas as pd
import numpy as np
import pvlib
from pvlib.tools import cosd
from pvlib import shading, irradiance

from ..design import ArrayDesign, FixedStructureDesign, TrackerStructureDesign


### -------------------------- SOLAR POSITION -------------------------- ###


def _pure_calculate_solar_position_table(
    location: Location,
    interval: pd.Interval,
):
    solar_position_table = location.get_solarposition(
        times=interval_to_index(interval),
        pressure=None,  # TODO: use actual pressure series
        temperature=12,  # TODO: use actual ambient temperature series
    )
    assert isinstance(solar_position_table, pd.DataFrame)
    solar_position_table.attrs['location'] = location
    solar_position_table.attrs['interval'] = interval
    return solar_position_table


def _solar_position_table(
    location: Location,
    interval: pd.Interval,
    context: ModelContext,
):
    """
    Calculates solar position and stores result in context for reuse
    This stored value is reused only if the same location and interval is requested
    """
    if '_solar_position_table' in context:
        result = context['_solar_position_table']
        assert isinstance(result, pd.DataFrame)
        if result.attrs['location'] is location and result.attrs['interval'] is interval:
            return result
    result = _pure_calculate_solar_position_table(location, interval)
    context['_solar_position_table'] = result
    return result


@standard_resource_type(R.solar_azimuth_angle, override_unit=True)
def pvlib_solar_azimuth_angle(context: ModelContext) -> pd.Series:
    solar_pos_table = context.run(_solar_position_table)
    return solar_pos_table['azimuth']


@standard_resource_type(R.solar_elevation_angle, override_unit=True)
def pvlib_solar_elevation_angle(context: ModelContext, apparent: bool = False) -> pd.Series:
    solar_pos_table = context.run(_solar_position_table)
    if apparent:
        return solar_pos_table['apparent_elevation']
    else:
        return solar_pos_table['elevation']


@standard_resource_type(R.solar_zenith_angle, override_unit=True)
def pvlib_solar_zenith_angle(context: ModelContext, apparent: bool = False) -> pd.Series:
    solar_pos_table = context.run(_solar_position_table)
    if apparent:
        return solar_pos_table['apparent_zenith']
    else:
        return solar_pos_table['zenith']


### -------------------------- ANGLE OF INCIDENCE -------------------------- ###


@standard_resource_type(R.tracker_rotation_angle, override_unit=True)
def pvlib_tracking_single_axis(
    apparent_zenith: Annotated[pd.Series, R.solar_zenith_angle(apparent=True)],
    apparent_azimuth: Annotated[pd.Series, R.solar_azimuth_angle],
    array: ArrayDesign,
) -> pd.Series:
    """
    Determine the rotation angle of a single-axis tracker when given particular
    solar zenith and azimuth angles.

    Based on pvlib.tracking.singleaxis, but ...
    https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.tracking.singleaxis.html
    """

    tracker = array.structure
    assert isinstance(tracker, TrackerStructureDesign), 'Project needs to have a tracker structure.'

    # extract array design parameters
    axis_tilt = tracker.axis_tilt
    axis_azimuth = tracker.axis_azimuth
    max_angle = tracker.max_tracking_angle
    backtrack = tracker.backtracking
    gcr = array.ground_cover_ratio

    # calculate cross axis tilt
    cross_axis_tilt = pvlib.tracking.calc_cross_axis_tilt(
        slope_azimuth=array.slope_azimuth,
        slope_tilt=array.slope_tilt,
        axis_azimuth=tracker.axis_azimuth,
        axis_tilt=tracker.axis_tilt,
    )

    # The ideal tracking angle, omega_ideal, is the rotation to place the sun
    # position vector (xp, yp, zp) in the (x, z) plane, which is normal to
    # the panel and contains the axis of rotation. omega_ideal=0 indicates
    # that the panel is horizontal. Here, our convention is that a clockwise
    # rotation is positive, to view rotation angles in the same frame of
    # reference as azimuth. For example, for a system with tracking
    # axis oriented south, a rotation toward the east is negative, and a
    # rotation to the west is positive. This is a right-handed rotation
    # around the tracker y-axis.
    omega_ideal = shading.projected_solar_zenith_angle(
        axis_tilt=axis_tilt,
        axis_azimuth=axis_azimuth,
        solar_zenith=apparent_zenith,
        solar_azimuth=apparent_azimuth,
    )

    # filter for sun above panel horizon
    zen_gt_90 = apparent_zenith > 90
    omega_ideal[zen_gt_90] = np.nan

    # Account for backtracking
    if backtrack:
        # distance between rows in terms of rack lengths relative to cross-axis
        # tilt
        axes_distance = 1 / (gcr * cosd(cross_axis_tilt))

        # NOTE: account for rare angles below array, see GH 824
        temp = np.abs(axes_distance * cosd(omega_ideal - cross_axis_tilt))

        # backtrack angle using [1], Eq. 14
        with np.errstate(invalid='ignore'):
            omega_correction = np.degrees(-np.sign(omega_ideal) * np.arccos(temp))

        # NOTE: in the middle of the day, arccos(temp) is out of range because
        # there's no row-to-row shade to avoid, & backtracking is unnecessary
        # [1], Eqs. 15-16
        with np.errstate(invalid='ignore'):
            tracker_theta = omega_ideal + np.where(temp < 1, omega_correction, 0)
    else:
        tracker_theta = omega_ideal

    # Clip tracker_theta between the minimum and maximum angles.
    min_angle = -max_angle
    tracker_theta = np.clip(tracker_theta, min_angle, max_angle)  # type: ignore

    # replace missing values with night stow angle
    tracker_theta: pd.Series
    tracker_theta.fillna(tracker.night_stow_angle * (-1), inplace=True)
    # NOTE: multiplying with -1 to make tracker face east at night (random choice)
    # TODO: replace night stow tilt angle with night stow rotation angle (theta) to allow users
    # to define orientation towards west as well

    return tracker_theta


def _tracker_orientation_table(
    tracker_rotation_angle: Annotated[pd.Series, R.tracker_rotation_angle], array: ArrayDesign
) -> pd.DataFrame:
    """
    wrapper for pvlib funtion
    pvlib.tracking.calc_surface_orientation
    only for trackers
    Two columns:
    surface tilt
    surface azimuth
    """
    tracker = array.structure
    assert isinstance(tracker, TrackerStructureDesign)

    tracker_orientation_table: pd.DataFrame = pvlib.tracking.calc_surface_orientation(
        tracker_theta=tracker_rotation_angle,
        axis_tilt=tracker.axis_tilt,  # type: ignore
        axis_azimuth=tracker.axis_azimuth,  # type: ignore
    )

    return tracker_orientation_table  # type: ignore


def _fixed_structure_orientation_table(array: ArrayDesign, interval: pd.Interval) -> pd.DataFrame:
    fixed = array.structure
    assert isinstance(fixed, FixedStructureDesign)
    fixed_structure_orientation_table = pd.DataFrame(
        {'surface_tilt': fixed.tilt, 'surface_azimuth': fixed.azimuth}, index=interval_to_index(interval)
    )
    return fixed_structure_orientation_table


@standard_resource_type(R.surface_tilt_angle, override_unit=True)
def pvlib_surface_tilt_angle(context: ModelContext, array: ArrayDesign):
    if isinstance(array.structure, TrackerStructureDesign):
        orientation_table = context.run(_tracker_orientation_table)
        return orientation_table['surface_tilt']

    else:
        orientation_table = context.run(_fixed_structure_orientation_table)
        return orientation_table['surface_tilt']


@standard_resource_type(R.surface_azimuth_angle, override_unit=True)
def pvlib_surface_azimuth_angle(context: ModelContext, array: ArrayDesign):
    if isinstance(array.structure, TrackerStructureDesign):
        orientation_table = context.run(_tracker_orientation_table)
        return orientation_table['surface_azimuth']

    else:
        orientation_table = context.run(_fixed_structure_orientation_table)
        return orientation_table['surface_azimuth']


@standard_resource_type(R.angle_of_incidence, override_unit=True)
def pvlib_angle_of_incidence(
    surface_tilt: Annotated[pd.Series, R.surface_tilt_angle],
    surface_azimuth: Annotated[pd.Series, R.surface_azimuth_angle],
    apparent_solar_zenith: Annotated[pd.Series, R.solar_zenith_angle(apparent=True)],
    solar_azimuth: Annotated[pd.Series, R.solar_azimuth_angle],
):
    """
    Wrapper around irradiance.aoi
    """
    aoi = irradiance.aoi(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        solar_zenith=apparent_solar_zenith,
        solar_azimuth=solar_azimuth,
    )
    return aoi
