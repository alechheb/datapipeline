__all__ = ["log_duration"]

import logging
import time
from datetime import timedelta
from functools import wraps

from typing import Any, Callable


logger = logging.getLogger(__name__)


def log_duration(func: Callable):
    """
    Times function call and log human readeable duration
    :param func: function to time
    :return: wrapper
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        started_at: float = time.monotonic()
        result: Any = func(*args, **kwargs)
        duration: timedelta = timedelta(
            milliseconds=1_000 * (time.monotonic() - started_at)
        )

        logger.debug("_exit %s - duration: %s", func.__qualname__, duration)
        return result

    return wrapper
