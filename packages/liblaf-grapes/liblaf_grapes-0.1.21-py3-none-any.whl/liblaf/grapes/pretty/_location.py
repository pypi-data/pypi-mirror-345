from pathlib import Path
from types import FrameType

from loguru._get_frame import get_frame
from rich.style import Style
from rich.text import Text

from liblaf.grapes.typed import PathLike


def location(
    name: str | None,
    function: str | None,
    line: int | None,
    file: PathLike | None = None,
) -> Text:
    text = Text()
    file: Path | None = Path(file or "<unknown>")
    function = function or "<unknown>"
    line = line or 0
    if file.exists():
        text.append(str(name), style=Style(link=file.as_uri()))
        text.append(":")
        text.append(f"{function}:{line}", style=Style(link=f"{file.as_uri()}#{line}"))
    else:
        text.append(f"{name}:{function}:{line}")
    return text


def caller_location(depth: int = 1) -> Text:
    frame: FrameType | None
    try:
        frame = get_frame(depth)
    except ValueError:
        frame = None
    file: str | None = None
    function: str | None = None
    line: int | None = None
    name: str | None = None
    if frame is not None:
        file = frame.f_code.co_filename
        function = frame.f_code.co_name
        line = frame.f_lineno
        name = frame.f_globals.get("__name__")
    text: Text = location(function=function, line=line, name=name, file=file)
    return text
