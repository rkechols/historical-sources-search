import logging
from abc import abstractmethod
from collections.abc import AsyncIterable
from typing import override
from urllib.parse import urljoin

from playwright.async_api import Browser, Locator, Page, expect as pw_expect

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.exceptions import MissingInformationError
from historical_sources_search.search_result import CollectionInfo, SearchResult


class CollectionBaseBrowserPaging(CollectionBase):
    def __init__(self, browser: Browser, collection_info: CollectionInfo, logger: logging.Logger | None):
        super().__init__(collection_info=collection_info)
        self.browser = browser
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    async def _enter_query(self, page: Page, query: str):
        """
        Enter the query into the collection's search function.
        No need to wait for results to fully load.
        """
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    def _get_locator_no_results(self, page: Page) -> Locator:
        """Construct a playwright locator to an element that indicates that the query has no results"""
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    def _get_locator_result_by_index(self, page: Page, index: int) -> Locator:
        """
        Construct a playwright locator to an element containing all the info for a single result on the current page.
        Parameter `index` indicates which result from many, with `index=0` indicating the first result.
        """
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    async def _get_result_url(self, page: Page, result_locator: Locator) -> str:
        """
        Get the URL of a single result (pointed to by `result_locator`).
        It's ok if the URL is relative.
        """
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    async def _get_result_title(self, page: Page, result_locator: Locator) -> str:
        """Get the title of a single result (pointed to by `result_locator`)"""
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    async def _get_result_detail(self, page: Page, result_locator: Locator) -> str | None:
        """Get the detail of a single result (pointed to by `result_locator`), if any"""
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    async def _get_result_image_src(self, page: Page, result_locator: Locator) -> str | None:
        """
        Get the source URL of a single result (pointed to by `result_locator`), if any.
        It's ok if the URL is relative.
        """
        raise NotImplementedError("Must be implemented by child class")

    @abstractmethod
    async def _advance_page(self, page: Page, current_page_index: int) -> bool:
        """
        Advance to the next page of search results.
        Parameter `current_page_index` indicates the current page displayed,
        with `current_page_index=0` indicating the first page of results is currently displayed.

        NOTE: this method should do its best to ensure the new page is fully loaded.

        If there are no more pages of results, return `False`.
        If the next page of results was successfully loaded, return `True`.
        """
        raise NotImplementedError("Must be implemented by child class")

    @override
    async def search(self, query: str) -> AsyncIterable[SearchResult]:
        async with (
            await self.browser.new_context() as browser_context,
            await browser_context.new_page() as page,
        ):
            await self._enter_query(page, query)

            locator_first_result = self._get_locator_result_by_index(page, 0)
            locator_no_results = self._get_locator_no_results(page)

            # wait for page to load either the first result or a "no result" element
            await pw_expect(locator_first_result.or_(locator_no_results).first).to_be_visible(timeout=30_000)
            if await locator_no_results.is_visible():
                self.logger.info(f"No results found for query {query!r}")
                return

            page_index = 0
            while True:  # turn through all pages
                self.logger.debug(f"Page number {page_index + 1} of query {query!r}")
                page_url = page.url

                i = 0
                while True:  # get all results from this page
                    result_locator = self._get_locator_result_by_index(page, i)
                    try:
                        await pw_expect(result_locator).to_be_visible(timeout=500)
                    except AssertionError:
                        break  # no more results on this page

                    try:
                        result_url = await self._get_result_url(page, result_locator)
                        result_url = urljoin(page_url, result_url)
                        result_title = await self._get_result_title(page, result_locator)
                        result_title = result_title.strip()
                        result_detail = await self._get_result_detail(page, result_locator)
                        if result_detail is not None:
                            result_detail = result_detail.strip()
                        result_image_src = await self._get_result_image_src(page, result_locator)
                        if result_image_src is not None:
                            result_image_src = urljoin(page_url, result_image_src)
                    except MissingInformationError:
                        self.logger.warning(
                            f"Skipping {page_index=} {i=} because of missing information",
                            exc_info=True,
                        )
                        # don't forget to increment `i` even though we're skipping this one
                    else:
                        yield SearchResult(
                            url=result_url,
                            title=result_title,
                            detail=result_detail,
                            image_src=result_image_src,
                            provided_by_collection=self.collection_info,
                        )
                    i += 1

                advance_success = await self._advance_page(page, page_index)
                if not advance_success:
                    break
                page_index += 1
