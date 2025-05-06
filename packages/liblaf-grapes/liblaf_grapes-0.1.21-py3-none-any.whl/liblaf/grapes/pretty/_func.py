from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal

import autoregistry
from rich.style import Style
from rich.text import Text

FUNC = autoregistry.Registry(prefix="_func_")


def func(obj: Callable, *, style: Literal["short", "long"] = "short") -> Text:
    return FUNC[style](obj)


@FUNC
def _func_short(obj: Callable) -> Text:
    text = Text()
    file: Path = Path(obj.__code__.co_filename)
    if file.exists():
        text.append(
            f"{obj.__name__}()",
            style=Style(link=f"{file.as_uri()}#{obj.__code__.co_firstlineno}"),
        )
    else:
        text.append(f"{obj.__name__}()")
    return text


@FUNC
def _func_long(obj: Callable) -> Text:
    text = Text()
    file: Path = Path(obj.__code__.co_filename)
    if file.exists():
        text.append(obj.__module__, style=Style(link=file.as_uri()))
        text.append(".")
        text.append(
            f"{obj.__qualname__}(...)",
            style=Style(link=f"{file.as_uri()}#{obj.__code__.co_firstlineno}"),
        )
    else:
        text.append(f"{obj.__module__}.{obj.__qualname__}(...)")
    return text


_pretty_func = func


def call(func: Callable, args: tuple, kwargs: Mapping) -> Text:  # noqa: ARG001
    # TODO: add `args` and `kwargs`
    return _pretty_func(func)
