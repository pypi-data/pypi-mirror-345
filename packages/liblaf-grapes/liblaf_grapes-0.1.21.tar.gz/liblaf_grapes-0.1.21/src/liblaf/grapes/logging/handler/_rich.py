from pathlib import Path
from typing import Unpack

import loguru
from environs import env
from rich.console import Console

from liblaf.grapes import pretty
from liblaf.grapes.logging.filters import Filter, make_filter
from liblaf.grapes.logging.sink import LoguruRichHandler, TracebackArgs
from liblaf.grapes.typed import PathLike


def rich_handler(
    *,
    console: Console | None = None,
    filter_: Filter | None = None,
    traceback: TracebackArgs | None = None,
    **kwargs: Unpack["loguru.BasicHandlerConfig"],
) -> "loguru.HandlerConfig":
    if console is None:
        console = pretty.get_console("stderr")
    filter_ = make_filter(filter_)
    if traceback is None:
        traceback = TracebackArgs(show_locals=True)
    return {
        "sink": LoguruRichHandler(console=console, traceback=traceback),
        "format": "",
        "filter": filter_,
        **kwargs,
    }


def file_handler(
    *,
    file: PathLike | None = None,
    filter_: Filter | None = None,
    traceback: TracebackArgs | None = None,
    **kwargs: Unpack["loguru.BasicHandlerConfig"],
) -> "loguru.HandlerConfig":
    if file is None:
        file = env.path("LOGGING_FILE", default=Path("run.log"))
    console: Console = pretty.get_console(file)
    filter_ = make_filter(filter_)
    if traceback is None:
        traceback = TracebackArgs(show_locals=True)
    return {
        "sink": LoguruRichHandler(console=console, traceback=traceback),
        "format": "",
        "filter": filter_,
        **kwargs,
    }
