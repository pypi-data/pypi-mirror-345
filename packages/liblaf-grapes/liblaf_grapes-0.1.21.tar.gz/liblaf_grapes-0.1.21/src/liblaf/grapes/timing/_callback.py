import functools
from typing import TYPE_CHECKING

from .typed import Callback

if TYPE_CHECKING:
    from ._base import TimerRecords


def log_record(
    index: int = -1,
    label: str | None = None,
    depth: int = 1,
    level: int | str = "DEBUG",
) -> Callback:
    return functools.partial(
        _log_record, index=index, label=label, depth=depth, level=level
    )


def log_summary(
    label: str | None = None,
    depth: int = 1,
    level: int | str = "INFO",
) -> Callback:
    return functools.partial(_log_summary, label=label, depth=depth, level=level)


def _log_record(
    timer: "TimerRecords",
    *,
    index: int = -1,
    label: str | None = None,
    depth: int = 1,
    level: int | str = "DEBUG",
) -> None:
    timer.log_record(index=index, label=label, depth=depth, level=level)


def _log_summary(
    timer: "TimerRecords",
    *,
    label: str | None = None,
    depth: int = 1,
    level: int | str = "INFO",
) -> None:
    timer.log_summary(label=label, depth=depth, level=level)
