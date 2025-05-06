import functools
from typing import IO, Literal

import rich
from environs import env
from rich.console import Console
from rich.style import Style
from rich.theme import Theme

from liblaf.grapes import path
from liblaf.grapes.typed import PathLike


def theme() -> Theme:
    return Theme(
        {
            "logging.level.notset": Style(dim=True),
            "logging.level.trace": Style(color="cyan", bold=True),
            "logging.level.debug": Style(color="blue", bold=True),
            "logging.level.icecream": Style(color="magenta", bold=True),
            "logging.level.info": Style(bold=True),
            "logging.level.success": Style(color="green", bold=True),
            "logging.level.warning": Style(color="yellow", bold=True),
            "logging.level.error": Style(color="red", bold=True),
            "logging.level.critical": Style(color="red", bold=True, reverse=True),
        },
        inherit=True,
    )


@functools.cache
def get_console(
    file: Literal["stdout", "stderr"] | IO | PathLike = "stdout", **kwargs
) -> Console:
    match file:
        case "stdout":
            rich.reconfigure(force_terminal=force_terminal(), theme=theme(), **kwargs)
            return rich.get_console()
        case "stderr":
            return Console(
                force_terminal=force_terminal(), theme=theme(), stderr=True, **kwargs
            )
        case IO():
            return Console(theme=theme(), file=file, **kwargs)
        case file:
            width: int = env.int("RICH_FILE_CONSOLE_WIDTH", default=120)
            return Console(
                theme=theme(), file=path.as_path(file).open("w"), width=width, **kwargs
            )


def force_terminal() -> bool | None:
    """...

    References:
        1. <https://force-color.org/>
        2. <https://no-color.org/>
    """
    if env.bool("FORCE_COLOR", None):
        return True
    if env.bool("NO_COLOR", None):
        return False
    if env.bool("GITHUB_ACTIONS", None):
        return True
    return None
