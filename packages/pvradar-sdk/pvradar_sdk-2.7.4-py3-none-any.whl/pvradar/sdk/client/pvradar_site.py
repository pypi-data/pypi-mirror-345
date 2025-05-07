import warnings
from typing import Any, Mapping, Optional, Self, override
from pvlib.location import Location

from .pvradar_validation import validate_pvradar_attrs
from ..modeling.basics import PvradarResourceType, Attrs
from ..modeling.geo_located_model_context import GeoLocatedModelContext
from ..modeling.library_manager import enrich_context_from_libraries
from ..pv.design import (
    ArrayDesign,
    ModuleDesign,
    StructureDesign,
    PvradarSiteDesign,
    make_fixed_design,
    get_azimuth_by_location,
    make_tracker_design,
)


class PvradarSite(GeoLocatedModelContext):
    def __init__(
        self,
        *,
        location: Optional[Location | tuple | str] = None,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        design: Optional[PvradarSiteDesign] = None,
        **kwargs,
    ) -> None:
        super().__init__(location=location, interval=interval, default_tz=default_tz, **kwargs)
        enrich_context_from_libraries(self)
        if design is not None:
            self.design = design

    def pvradar_resource_type(self, resource_type: PvradarResourceType, *, attrs: Optional[Attrs] = None, **kwargs):
        warnings.warn(
            '.pvradar_resource_type() is deprecated, use .resource(attrs(resource_type=...)) instead', DeprecationWarning
        )
        req: dict[str, Any] = {'resource_type': resource_type}
        if attrs:
            new_req = dict(attrs.copy())
            new_req.update(req)
            req = new_req

        return self.resource(req, **kwargs)

    @override
    def _convert_by_attrs(self, value: Any, param_attrs: Mapping[str, Any]) -> Any:
        if not self.config.get('disable_validation'):
            validate_pvradar_attrs(param_attrs)
        return super()._convert_by_attrs(value, param_attrs)

    @property
    def design(self) -> PvradarSiteDesign:
        return self.resource('design')

    @design.setter
    def design(self, value: PvradarSiteDesign):
        if not isinstance(value, PvradarSiteDesign):
            raise ValueError(f'While setting design expected PvradarSiteDesign, got {value.__class__.__name__}')
        self['design'] = value

    @property
    def array(self) -> ArrayDesign:
        return self.design.array

    @property
    def module(self) -> ModuleDesign:
        return self.array.module

    @property
    def structure(self) -> StructureDesign:
        return self.array.structure

    @override
    def __repr__(self):
        return f'Pvradar site at ({self.location}) with interval {self.interval}'

    @classmethod
    def as_fixed_array(
        cls,
        *,
        # site parameters
        location: Location | tuple | str,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        #
        # structure parameters
        tilt: float = 20,
        azimuth: Optional[float] = None,
        clearance: float = 1,
        #
        # common design parameters
        module_rated_power: float = 400,
        dc_capacity: float = 100 * 1e6,  # 100 MW
        dc_ac_ratio: float = 1.2,
        module_placement='2v',
    ) -> Self:
        """convenience method creating site with a single fixed array in one call"""
        instance = cls(
            location=location,
            interval=interval,
            default_tz=default_tz,
        )
        if azimuth is None:
            azimuth = get_azimuth_by_location(instance.location)
        design = make_fixed_design(
            tilt=tilt,
            azimuth=azimuth,
            clearance=clearance,
            #
            # common design parameters
            module_rated_power=module_rated_power,
            dc_capacity=dc_capacity,
            dc_ac_ratio=dc_ac_ratio,
            module_placement=module_placement,
        )
        instance.design = design
        return instance

    @classmethod
    def as_tracker_array(
        cls,
        *,
        # site parameters
        location: Location | tuple | str,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        #
        # structure parameters
        axis_height: float = 1.5,
        axis_azimuth: float = 0,
        axis_tilt: float = 0,
        max_tracking_angle: float = 60,
        night_stow_angle: float = 0,
        backtracking: bool = True,
        #
        # common design parameters
        module_rated_power: float = 400,
        dc_capacity: float = 100 * 1e6,  # 100 MW
        dc_ac_ratio: float = 1.2,
        module_placement='2v',
    ) -> Self:
        """convenience method creating site with a single array with a tracker in one call"""
        instance = cls(
            location=location,
            interval=interval,
            default_tz=default_tz,
        )
        design = make_tracker_design(
            axis_height=axis_height,
            axis_azimuth=axis_azimuth,
            axis_tilt=axis_tilt,
            max_tracking_angle=max_tracking_angle,
            night_stow_angle=night_stow_angle,
            backtracking=backtracking,
            #
            # common design parameters
            module_rated_power=module_rated_power,
            dc_capacity=dc_capacity,
            dc_ac_ratio=dc_ac_ratio,
            module_placement=module_placement,
        )
        instance.design = design
        return instance
