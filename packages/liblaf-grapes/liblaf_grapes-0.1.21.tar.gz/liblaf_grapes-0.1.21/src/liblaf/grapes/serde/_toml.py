from pathlib import Path
from typing import Any, override

import tomlkit

from liblaf.grapes import path
from liblaf.grapes.typed import PathLike

from ._abc import AbstractSerializer


class TOMLSerializer(AbstractSerializer):
    @override
    def load(self, fpath: PathLike, **kwargs) -> tomlkit.TOMLDocument:
        fpath: Path = path.as_path(fpath)
        with fpath.open() as fp:
            return tomlkit.load(fp, **kwargs)

    @override
    def loads(self, data: str, **kwargs) -> tomlkit.TOMLDocument:
        return tomlkit.loads(data, **kwargs)

    @override
    def save(self, fpath: PathLike, data: Any, **kwargs) -> None:
        fpath: Path = path.as_path(fpath)
        with fpath.open("w") as fp:
            tomlkit.dump(data, fp, **kwargs)

    @override
    def saves(self, data: Any, **kwargs) -> str:
        return tomlkit.dumps(data, **kwargs)


toml = TOMLSerializer()
load_toml = toml.load
loads_toml = toml.loads
save_toml = toml.save
saves_toml = toml.saves
