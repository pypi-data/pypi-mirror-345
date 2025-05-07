import orjson
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional, TypedDict, NotRequired, override

from ..modeling.measurement_schemas import MeasurementManifest

default_encoding = 'utf8'


class ReadFileOpRecipe(TypedDict):
    op: str
    path: str | Path
    encoding: NotRequired[str]


class AbstractSource(ABC):
    @abstractmethod
    def get_file_contents(self, path: str | Path, encoding: Optional[str] = default_encoding) -> str:
        pass

    @abstractmethod
    def check_file_exists(self, path: str | Path) -> bool:
        pass

    def to_op(self) -> Callable:
        def read_file(op_recipe: dict[str, Any], value: Any = None) -> str:
            assert 'path' in op_recipe, 'path is required in op_recipe'
            return self.get_file_contents(op_recipe['path'], getattr(op_recipe, 'encoding', default_encoding))

        return read_file

    def get_measurement_manifest(self) -> MeasurementManifest | None:
        if not self.check_file_exists('measurements.json'):
            return None
        raw = self.get_file_contents('measurements.json')
        raw_dict = orjson.loads(raw)
        return MeasurementManifest(**raw_dict)


class LocalSource(AbstractSource):
    def __init__(self, dir: str | Path) -> None:
        self.dir = Path(dir)

    def _get_full_path(self, path: str | Path) -> Path:
        return Path.joinpath(self.dir, path)

    @override
    def get_file_contents(self, path: str | Path, encoding: Optional[str] = default_encoding) -> str:
        with open(self._get_full_path(path), 'r', encoding=encoding) as f:
            return f.read()

    @override
    def check_file_exists(self, path: str | Path) -> bool:
        return self._get_full_path(path).exists()
