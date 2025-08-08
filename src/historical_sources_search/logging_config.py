import logging
import logging.config
from typing import override


class FilterLessThanLevel(logging.Filter):
    """
    Logging filter that only allows records with a level *less than* the specified level
    (general usage of logging levels only allow records with a level *greater than or equal to* the specified level)
    """

    @override
    def __init__(self, level: int):
        """
        Construct an instance.

        Parameters
        ----------
        level: only logs with a level less than this will be allowed through the filter
            e.g. logging.WARNING (30) will allow logging.DEBUG (10) and logging.INFO (20) records
        """
        super().__init__()
        self.level = level

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


VERBOSE_LOGGERS = {
    "__main__",
    "__mp_main__",
    "historical_sources_search",
}


def init_logging():
    """
    Initialize the logging system.

    Sets up the logging system with a default configuration which:
    - generally suppresses logs with level below `WARNING`, but loggers listed in `VERBOSE_LOGGERS` are set to `DEBUG`
    - log records with level less than `WARNING` go to stdout
    - log records with level `WARNING` or higher go to stderr
    """
    explicit_logger_levels: dict[str, int] = dict.fromkeys(VERBOSE_LOGGERS, logging.DEBUG)
    config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "filters": {
            "less_than_warning": {
                "()": FilterLessThanLevel,
                "level": logging.WARNING,
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
                "level": logging.DEBUG,
                "filters": ["less_than_warning"],
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "default",
                "level": logging.WARNING,
            },
        },
        "loggers": {
            logger_name: {"level": explicit_level} for logger_name, explicit_level in explicit_logger_levels.items()
        },
        "root": {
            "level": logging.WARNING,  # inherited by loggers that otherwise don't have their level set
            "handlers": ["stderr", "stdout"],
        },
        "disable_existing_loggers": False,  # allow loggers to be instantiated before this config
    }
    logging.config.dictConfig(config)
