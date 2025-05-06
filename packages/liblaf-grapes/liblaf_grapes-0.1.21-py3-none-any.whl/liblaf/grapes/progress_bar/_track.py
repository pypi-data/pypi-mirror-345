from collections.abc import Generator, Iterable, Sequence

from rich.progress import Progress

from liblaf.grapes import timing
from liblaf.grapes.timing import TimerName
from liblaf.grapes.typed import MISSING, MissingType

from ._progress import progress


def track[T](
    iterable: Iterable[T],
    *,
    description: str = "Progress",
    timers: bool | Sequence[TimerName | str] = ["perf"],
    total: float | None = None,
    callback_end: timing.Callback | MissingType | None = MISSING,
    callback_finally: timing.Callback | MissingType | None = MISSING,
) -> Generator[T]:
    prog: Progress = progress()
    if timers is True:
        timers = ["perf"]
    if total is None:
        total = try_len(iterable)
    if timers:
        if callback_end is MISSING:
            callback_end = timing.log_record(depth=6)
        if callback_finally is MISSING:
            callback_finally = timing.log_summary(depth=5)
        iterable: timing.TimedIterable[T] = timing.timer(
            iterable,
            label=description,
            timers=timers,
            callback_end=callback_end,
            callback_finally=callback_finally,
            total=int(total) if total is not None else None,
        )
        with prog:
            yield from prog.track(iterable, total=total, description=description)
    else:
        with prog:
            yield from prog.track(iterable, total=total, description=description)


def try_len(iterable: Iterable) -> int | None:
    try:
        return len(iterable)  # pyright: ignore[reportArgumentType]
    except TypeError:
        return None
