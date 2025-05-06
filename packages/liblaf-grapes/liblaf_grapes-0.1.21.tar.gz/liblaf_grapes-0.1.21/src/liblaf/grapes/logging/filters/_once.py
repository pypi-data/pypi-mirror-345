from collections.abc import Callable, Hashable, Sequence

import glom
import loguru

DEFAULT_SPECS: Sequence[str] = (
    "file.path",
    "function",
    "level.no",
    "line",
    "message",
    "module",
    "name",
)


def default_transform(record: "loguru.Record") -> Hashable:
    return tuple(glom.glom(record, spec) for spec in DEFAULT_SPECS)


def filter_once(
    transform: "Callable[[loguru.Record], Hashable]" = default_transform,
) -> "loguru.FilterFunction":
    history: set[Hashable] = set()

    def filter_(record: "loguru.Record") -> bool:
        if not record["extra"].get("once", False):
            return True
        transformed: Hashable = transform(record)
        if transformed in history:
            return False
        history.add(transformed)
        return True

    return filter_
