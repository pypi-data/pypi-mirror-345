from rich.console import Console, RenderableType
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Column
from rich.text import Text

from liblaf.grapes import human as _human
from liblaf.grapes import pretty


class RateColumn(ProgressColumn):
    """RateColumn is a subclass of ProgressColumn that represents the rate of progress for a given task."""

    unit: str = "it"
    """The unit of measurement for the progress bar."""

    def __init__(self, unit: str = "it", table_column: Column | None = None) -> None:
        """.

        Args:
            unit: The unit of measurement for the progress bar.
            table_column: The table column associated with the progress bar.
        """
        super().__init__(table_column)
        self.unit = unit

    def render(self, task: Task) -> RenderableType:
        """Render the progress speed of a given task.

        Args:
            task: The task for which the speed is to be rendered.

        Returns:
            A text object representing the speed of the task.
        """
        if not task.speed:
            return Text(f"?{self.unit}/s", style="progress.data.speed")
        human: str = _human.human_throughout(task.speed, self.unit)
        return Text(human, style="progress.data.speed")


def progress(
    *columns: str | ProgressColumn, console: Console | None = None
) -> Progress:
    """Create and return a Progress instance with specified columns and console.

    If no columns are provided, a default set of columns will be used:

    - `SpinnerColumn`
    - `TextColumn` with task description
    - `BarColumn`
    - `TaskProgressColumn` with speed display
    - `MofNCompleteColumn`
    - `TimeElapsedColumn`
    - `TimeRemainingColumn`
    - `RateColumn`

    Args:
        *columns: Variable length argument list of columns to include in the progress display.
        console: The console to use for rendering the progress. Defaults to `None`, in which case the logging console is used.

    Returns:
        An instance of the Progress class configured with the specified columns and console.
    """
    if not columns:
        columns: list[ProgressColumn] = [SpinnerColumn()]
        columns.append(TextColumn("[progress.description]{task.description}"))
        columns += [
            BarColumn(),
            TaskProgressColumn(show_speed=True),
            MofNCompleteColumn(),
            "[",
            TimeElapsedColumn(),
            "<",
            TimeRemainingColumn(),
            ",",
            RateColumn(),
            "]",
        ]
    console = console or pretty.get_console("stderr")
    progress = Progress(*columns, console=console)
    return progress
