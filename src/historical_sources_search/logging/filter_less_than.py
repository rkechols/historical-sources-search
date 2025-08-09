import logging
from typing import override


class FilterLessThanLevel(logging.Filter):
    """
    Logging filter that only allows records with a level *less than* the specified level
    (general usage of logging levels only allow records with a level *greater than or equal to* the specified level)
    """

    @override
    def __init__(self, level: int | str):
        """
        Construct an instance.

        Parameters
        ----------
        level: only logs with a level less than this will be allowed through the filter
            e.g. logging.WARNING (30) will allow logging.DEBUG (10) and logging.INFO (20) records
        """
        super().__init__()
        self.level: int = level if isinstance(level, int) else getattr(logging, level.upper())

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Decide if a log record should be allowed through the filter.

        Called directly by the logging system

        Returns
        -------
        True if the log record should be allowed through the filter, False otherwise
        """
        return record.levelno < self.level
