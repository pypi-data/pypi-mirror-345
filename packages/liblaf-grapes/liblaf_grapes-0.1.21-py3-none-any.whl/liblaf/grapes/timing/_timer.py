import contextlib
import types
from collections.abc import Callable, Iterable, Sequence
from typing import Self, overload

import attrs

from liblaf.grapes.typed import MISSING, MissingType

from ._base import TimerRecords
from ._callback import log_record
from ._function import TimedFunction
from ._iterable import TimedIterable
from ._time import TimerName
from .typed import Callback


@attrs.define
class Timer(
    contextlib.AbstractAsyncContextManager,
    contextlib.AbstractContextManager,
    TimerRecords,
):
    async def __aenter__(self) -> Self:
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None:
        return self.__exit__(exc_type, exc_value, traceback)

    def __call__[**P, T](self, func: Callable[P, T]) -> TimedFunction[P, T]:
        return TimedFunction(
            func,
            label=self.label,
            timers=self.timers,
            callback_start=self.callback_start,
            callback_end=self.callback_end,
            callback_finally=self.callback_finally,
        )

    def __enter__(self) -> Self:
        if self.label is None:
            self.label = "With Block"
        if self.callback_end is MISSING:
            self.callback_end = log_record(depth=4)
        self._start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None:
        self._end()

    def start(self) -> None:
        self._start()

    def end(self) -> None:
        self._end()


@overload
def timer[T](
    iterable: Iterable[T],
    *,
    label: str | None = None,
    timers: Sequence[TimerName | str] = ["perf"],
    callback_start: Callback | MissingType | None = MISSING,
    callback_end: Callback | MissingType | None = MISSING,
    callback_finally: Callback | MissingType | None = MISSING,
    total: int | None = None,
) -> TimedIterable[T]: ...
@overload
def timer(
    *,
    label: str | None = None,
    timers: Sequence[TimerName | str] = ["perf"],
    callback_start: Callback | MissingType | None = MISSING,
    callback_end: Callback | MissingType | None = MISSING,
    callback_finally: Callback | MissingType | None = MISSING,
) -> Timer: ...
def timer[T](
    iterable: Iterable[T] | None = None,
    *,
    label: str | None = None,
    timers: Sequence[TimerName | str] = ["perf"],
    callback_start: Callback | MissingType | None = MISSING,
    callback_end: Callback | MissingType | None = MISSING,
    callback_finally: Callback | MissingType | None = MISSING,
    total: int | None = None,
) -> TimedIterable[T] | Timer:
    if iterable is not None:
        return TimedIterable(
            iterable=iterable,
            label=label,
            timers=timers,
            callback_start=callback_start,
            callback_end=callback_end,
            callback_finally=callback_finally,
            total=total,
        )
    return Timer(
        label=label,
        timers=timers,
        callback_start=callback_start,
        callback_end=callback_end,
        callback_finally=callback_finally,
    )
