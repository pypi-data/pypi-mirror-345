from collections.abc import Iterable, Iterator

import attrs

from liblaf.grapes.typed import MISSING, MissingType

from ._base import TimerRecords
from ._callback import log_record, log_summary
from ._utils import default_if_missing
from .typed import Callback


@attrs.define
class TimedIterable[T](TimerRecords):
    callback_end: Callback | MissingType | None = attrs.field(
        default=MISSING,
        converter=default_if_missing(log_record(depth=4)),
        kw_only=True,
    )
    callback_finally: Callback | MissingType | None = attrs.field(
        default=MISSING,
        converter=default_if_missing(log_summary(depth=3)),
        kw_only=True,
    )
    total: int | None = attrs.field(default=None, kw_only=True)
    _iterable: Iterable[T] = attrs.field(
        alias="iterable", on_setattr=attrs.setters.frozen
    )

    def __attrs_post_init__(self) -> None:
        self.label = self.label or "Iterable"

    def __contains__(self, x: object, /) -> bool:
        return x in self._iterable  # pyright: ignore[reportOperatorIssue]

    def __iter__(self) -> Iterator[T]:
        for item in self._iterable:
            self._start()
            yield item
            self._end()
        if callable(self.callback_finally):
            self.callback_finally(self)

    def __len__(self) -> int:
        if self.total is not None:
            return self.total
        return len(self._iterable)  # pyright: ignore[reportArgumentType]
