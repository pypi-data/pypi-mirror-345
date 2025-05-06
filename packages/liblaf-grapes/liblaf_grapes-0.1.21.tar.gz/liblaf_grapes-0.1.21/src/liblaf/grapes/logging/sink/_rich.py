import datetime
import types
from typing import Self, TypedDict

import attrs
import loguru
from rich.console import Console, RenderableType
from rich.highlighter import Highlighter, ReprHighlighter
from rich.table import Table
from rich.text import Text
from rich.traceback import Traceback

from liblaf.grapes import pretty


class TracebackArgs(TypedDict, total=False):
    show_locals: bool


@attrs.frozen(kw_only=True)
class RichLogRecordRenderer:
    console: Console = attrs.field(factory=lambda: pretty.get_console("stderr"))
    highlighter: Highlighter = attrs.field(factory=ReprHighlighter)
    markup: bool = attrs.field(default=True)
    traceback: TracebackArgs = attrs.field(
        factory=lambda: TracebackArgs(show_locals=True)
    )

    row: list[RenderableType] = attrs.field(init=False, factory=list)
    table: Table = attrs.field(
        init=False, factory=lambda: Table.grid(padding=(0, 1), expand=True)
    )

    def add_time(self, record: "loguru.Record") -> Self:
        self.table.add_column("Time", style="log.time")
        elapsed: datetime.timedelta = record["elapsed"]
        hh: int
        mm: int
        ss: int
        mm, ss = divmod(int(elapsed.total_seconds()), 60)
        hh, mm = divmod(mm, 60)
        self.row.append(f"{hh:02}:{mm:02}:{ss:02}.{elapsed.microseconds:06d}")
        return self

    def add_level(self, record: "loguru.Record") -> Self:
        self.table.add_column("Level", style="log.level", width=8)
        level: str = record["level"].name
        self.row.append(Text(level, style=f"logging.level.{level.lower()}"))
        return self

    def add_message(self, record: "loguru.Record") -> Self:
        self.table.add_column("Message", style="log.message", ratio=1)
        if (rich := record["extra"].get("rich")) is not None:
            self.row.append(rich)
            return self
        message: RenderableType = record["message"].rstrip()
        if record["extra"].get("markup", self.markup):
            message = Text.from_markup(message)
        if highlighter := record["extra"].get("highlighter", self.highlighter):
            message = highlighter(message)
        self.row.append(message)
        return self

    def add_path(self, record: "loguru.Record") -> Self:
        self.table.add_column("Path", style="log.path")
        path: Text = pretty.location(
            name=record["name"],
            function=record["function"],
            line=record["line"],
            file=record["file"].path,
        )
        self.row.append(path)
        return self

    def render_exception(self, record: "loguru.Record") -> RenderableType | None:
        exception: loguru.RecordException | None = record["exception"]
        if exception is None:
            return None
        exc_type: type[BaseException] | None
        exc_value: BaseException | None
        traceback: types.TracebackType | None
        exc_type, exc_value, traceback = exception
        if exc_type is None or exc_value is None:
            return None
        return Traceback.from_exception(
            exc_type=exc_type,
            exc_value=exc_value,
            traceback=traceback,
            width=self.console.width,
            code_width=self.console.width,
            **self.traceback,
        )

    def render(self) -> RenderableType:
        self.table.add_row(*self.row)
        return self.table


@attrs.define(kw_only=True)
class LoguruRichHandler:
    console: Console = attrs.field(factory=lambda: pretty.get_console("stderr"))
    highlighter: Highlighter = attrs.field(factory=ReprHighlighter)
    markup: bool = attrs.field(default=True)
    traceback: TracebackArgs = attrs.field(
        factory=lambda: TracebackArgs(show_locals=True)
    )

    def __call__(self, message: "loguru.Message") -> None:
        renderer = RichLogRecordRenderer(
            console=self.console,
            highlighter=self.highlighter,
            markup=self.markup,
            traceback=self.traceback,
        )
        renderer.add_time(message.record)
        renderer.add_level(message.record)
        renderer.add_message(message.record)
        renderer.add_path(message.record)
        # TODO: console.print() is extremely slow
        self.console.print(renderer.render())
        if (exception := renderer.render_exception(message.record)) is not None:
            self.console.print(exception)
