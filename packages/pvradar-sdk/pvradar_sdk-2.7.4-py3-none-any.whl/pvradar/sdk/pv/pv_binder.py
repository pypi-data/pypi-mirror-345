from typing import Any, Optional, override

from .design import PvradarSiteDesign
from ..modeling.geo_located_model_context import GeoLocatedModelContext
from ..modeling.basics import BindingNotFound, ModelParam
from ..modeling.model_context import ModelContext
from ..modeling.model_wrapper import ModelBinding
from ..modeling.model_binder import AbstractBinder
from .irradiance import pvlib_irradiance_perez_driesse

_known_properties = [
    'array',
    'module',
    'structure',
]


class PvBinder(AbstractBinder):
    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any:
        assert isinstance(context, GeoLocatedModelContext), (
            f'PvBinder requires a GeoLocatedModelContext, got {context.__class__.__name__}'
        )
        if resource_name in _known_properties:
            return getattr(context, resource_name)

        if resource_name == 'sky_diffuse_poa_on_front':
            if not context:
                return BindingNotFound
            model = context.wrap_model(pvlib_irradiance_perez_driesse)
            return ModelBinding(model=model, defaults=defaults or {})
        if as_param and as_param.type:
            if as_param.type == PvradarSiteDesign:
                assert hasattr(context, 'design'), (
                    'PvradarSiteDesign requires context.attrs, but {context.__class__.__name__} does not have it'
                )
                return getattr(context, 'design')
        if as_param and as_param.attrs:
            attrs = as_param.attrs
            if attrs.get('resource_type') == 'design':
                return getattr(context, 'design')
        return BindingNotFound
