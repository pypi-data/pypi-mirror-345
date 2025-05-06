from collections.abc import Callable
from typing import Any, overload

from liblaf.grapes.typed import MISSING


@overload
def default_if_missing(default: Any = MISSING) -> Callable[[Any], Any]: ...
@overload
def default_if_missing(*, factory: Callable) -> Callable[[Any], Any]: ...
def default_if_missing(
    default: Any = MISSING, factory: Callable | None = None
) -> Callable[[Any], Any]:
    if default is MISSING:

        def converter(val: Any) -> Any:
            if val is MISSING:
                return factory()  # pyright: ignore[reportOptionalCall]
            return val
    else:

        def converter(val: Any) -> Any:
            if val is MISSING:
                return default
            return val

    return converter
