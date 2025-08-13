import asyncio
import logging
from collections import deque
from collections.abc import AsyncIterable

import httpx
from playwright.async_api import Browser

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.collections.facing_history import CollectionFacingHistory
from historical_sources_search.collections.library_of_congress import CollectionLibraryOfCongress
from historical_sources_search.env import Env
from historical_sources_search.search_result import SearchResult

LOGGER = logging.getLogger(__name__)


async def _search_worker(query: str, *, collections: deque[CollectionBase], results_queue: asyncio.Queue[SearchResult]):
    while True:
        try:
            collection = collections.popleft()
        except IndexError:  # `collections` is empty
            break
        async for result in collection.search(query):
            await results_queue.put(result)


async def search_all(query: str, httpx_client: httpx.AsyncClient, browser: Browser) -> AsyncIterable[SearchResult]:
    LOGGER.debug(f"{httpx_client = }")

    collections: deque[CollectionBase] = deque(
        [
            CollectionFacingHistory(browser),
            CollectionLibraryOfCongress(browser),
            # TODO: add more collections
        ]
    )
    results_queue = asyncio.Queue[SearchResult]()

    async def _run_workers():
        async with asyncio.TaskGroup() as tg:
            for _ in range(Env.get().n_search_workers):
                tg.create_task(_search_worker(query, collections=collections, results_queue=results_queue))
            # the `asyncio.TaskGroup` context manager waits for workers to finish before closing
        results_queue.shutdown()

    task_run_workers = asyncio.create_task(_run_workers())

    while True:
        try:
            result = await results_queue.get()
        except asyncio.QueueShutDown:
            break
        yield result

    task_run_workers.result()
