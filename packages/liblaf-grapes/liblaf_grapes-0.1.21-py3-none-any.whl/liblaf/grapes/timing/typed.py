from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ._base import TimerRecords


class Callback(Protocol):
    def __call__(self, timer: "TimerRecords") -> None: ...
