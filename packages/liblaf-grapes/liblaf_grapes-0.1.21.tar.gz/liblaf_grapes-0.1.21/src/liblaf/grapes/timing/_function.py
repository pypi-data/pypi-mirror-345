import functools
from collections.abc import Callable

import attrs

from liblaf.grapes import pretty
from liblaf.grapes.typed import MISSING, MissingType

from ._base import TimerRecords
from ._callback import log_record
from ._utils import default_if_missing
from .typed import Callback


# `slots=False` is required to make `functools.update_wrapper(...)` work
# ref: <https://www.attrs.org/en/stable/glossary.html#term-slotted-classes>
@attrs.define(slots=False)
class TimedFunction[**P, T](TimerRecords):
    callback_end: Callback | MissingType | None = attrs.field(
        default=MISSING, converter=default_if_missing(log_record(depth=4)), kw_only=True
    )
    _func: Callable[P, T] = attrs.field(alias="func", on_setattr=attrs.setters.frozen)

    def __attrs_post_init__(self) -> None:
        self.label = self.label or pretty.func(self._func).plain or "Function"
        functools.update_wrapper(self, self._func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        self._start()
        result: T = self._func(*args, **kwargs)
        self._end()
        return result
