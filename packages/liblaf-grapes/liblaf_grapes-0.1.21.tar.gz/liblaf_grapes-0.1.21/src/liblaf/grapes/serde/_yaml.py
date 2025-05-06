import io
from pathlib import Path
from typing import Any, override

from ruamel.yaml import YAML

from liblaf.grapes import path
from liblaf.grapes.typed import PathLike

from ._abc import AbstractSerializer


class YAMLSerializer(AbstractSerializer):
    @override
    def load(self, fpath: PathLike, **kwargs) -> Any:
        fpath: Path = path.as_path(fpath)
        yaml = YAML(**kwargs)
        with fpath.open() as fp:
            return yaml.load(fp)

    @override
    def loads(self, data: str, **kwargs) -> Any:
        stream = io.StringIO(data)
        yaml = YAML(**kwargs)
        return yaml.load(stream)

    @override
    def save(self, fpath: PathLike, data: Any, **kwargs) -> None:
        fpath: Path = path.as_path(fpath)
        yaml = YAML(**kwargs)
        with fpath.open("w") as fp:
            yaml.dump(data, fp)

    @override
    def saves(self, data: Any, **kwargs) -> str:
        stream = io.StringIO()
        yaml = YAML(**kwargs)
        yaml.dump(data, stream)
        return stream.getvalue()


yaml = YAMLSerializer()
load_yaml = yaml.load
loads_yaml = yaml.loads
save_yaml = yaml.save
saves_yaml = yaml.saves
