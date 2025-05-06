import logging
from collections.abc import Sequence

import loguru

from ._icecream import init_icecream
from ._init_loguru import init_loguru
from .filters import Filter


def init_logging(
    level: int | str = logging.NOTSET,
    *,
    filter_: Filter | None = None,
    handlers: Sequence["loguru.HandlerConfig"] | None = None,
    levels: Sequence["loguru.LevelConfig"] | None = None,
) -> None:
    init_loguru(level=level, filter_=filter_, handlers=handlers, levels=levels)
    init_icecream()
