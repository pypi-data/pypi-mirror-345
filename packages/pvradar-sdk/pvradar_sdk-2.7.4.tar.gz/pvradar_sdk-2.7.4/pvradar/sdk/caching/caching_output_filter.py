from typing import Any, Callable

from ..modeling.base_model_context import BaseModelContext
from ..modeling.basics import ModelParam
from .advisor.caching_advisor import CachingAdvisor
from .kv_storage.kv_storage_adaptor import KVStorageAdaptor
from ..modeling.model_wrapper import ModelWrapper


class CachingOutputFilter:
    def __init__(self, key_maker: Callable, kv_storage: KVStorageAdaptor, advisor: CachingAdvisor, context: BaseModelContext):
        self.key_maker = key_maker
        self.kv_storage = kv_storage
        self.advisor = advisor
        self.context = context

    def __call__(self, model_wrapper: ModelWrapper, bound_params: dict[str, Any], result: Any) -> Any:
        if self.advisor.should_save(
            model_wrapper=model_wrapper,
            result=result,
            context=self.context,
        ):
            resource_name = '_anonymous'
            model_param = ModelParam(
                name=resource_name,
                annotation=result.__class__,
                attrs=result.attrs,
                type=result.__class__,
            )

            key = self.key_maker(resource_name=resource_name, as_param=model_param, context=self.context)
            if key and not self.kv_storage.key_exists(key):
                self.kv_storage.serialize_and_save(key, result)
        return result
