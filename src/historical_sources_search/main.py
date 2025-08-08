import logging

from historical_sources_search.env import Env
from historical_sources_search.logging_config import init_logging

init_logging()

LOGGER = logging.getLogger(__name__)


def main() -> None:
    env = Env.get()
    LOGGER.debug(f"{env.playwright_debug = }")
