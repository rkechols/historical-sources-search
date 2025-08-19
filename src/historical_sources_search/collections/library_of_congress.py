import logging
from typing import override
from urllib.parse import urlencode

from playwright.async_api import Browser, Locator, Page, TimeoutError as PlaywrightTimeoutError, expect as pw_expect

from historical_sources_search.collections.base_browser_paging import CollectionBaseBrowserPaging
from historical_sources_search.exceptions import MissingInformationError, NavigationError
from historical_sources_search.search_result import CollectionInfo

LOGGER = logging.getLogger(__name__)


class CollectionLibraryOfCongress(CollectionBaseBrowserPaging):
    def __init__(self, browser: Browser):
        super().__init__(
            browser=browser,
            collection_info=CollectionInfo(
                name="Classroom Materials at the Library of Congress",
                url="https://www.loc.gov/classroom-materials/?fa=partof_type%3Aprimary+source+set",
            ),
        )

    @override
    async def _enter_query(self, page: Page, query: str):
        url_params = urlencode(
            {
                "q": query,
                "fa": "partof_type:primary source set",
                "st": "list",
                # "c": "150",  # results per page
            }
        )
        search_url = f"https://www.loc.gov/classroom-materials/?{url_params}"
        LOGGER.debug(f"Search url: {search_url}")
        response = await page.goto(search_url)
        if response is not None and not response.ok:
            raise NavigationError(f"Navigation to `{search_url}` failed with status {response.status}")

    @override
    def _get_locator_no_results(self, page: Page) -> Locator:
        return page.locator(".noresults-for")

    @override
    def _get_locator_result_by_index(self, page: Page, index: int) -> Locator:
        return page.locator("[id=results]").locator("li.item").nth(index)

    @override
    async def _get_result_url(self, page: Page, result_locator: Locator) -> str:
        item_title = result_locator.locator(".item-description-title").locator("a")
        item_title_href = await item_title.get_attribute("href")
        if not item_title_href:
            item_title_html = await item_title.inner_html()
            raise MissingInformationError(f"Search result did not have an href: {item_title_html}")
        return item_title_href

    @override
    async def _get_result_title(self, page: Page, result_locator: Locator) -> str:
        return await result_locator.locator(".item-description-title").locator("a").inner_text()

    @override
    async def _get_result_detail(self, page: Page, result_locator: Locator) -> str | None:
        return await result_locator.locator(".item-description-abstract").inner_text()

    @override
    async def _get_result_image_src(self, page: Page, result_locator: Locator) -> str | None:
        item_image = result_locator.locator("figure").locator("img")
        try:
            return await item_image.get_attribute("src", timeout=500)
        except PlaywrightTimeoutError:
            return None

    @override
    async def _advance_page(self, page: Page, current_page_index: int) -> bool:
        current_page_number = current_page_index + 1
        next_page_button = page.get_by_role("link", name="Next Page")
        try:
            await pw_expect(next_page_button).to_be_visible(timeout=1_000)
        except AssertionError:
            return False  # no more pages
        await next_page_button.click()
        new_page_number = current_page_number + 1
        await pw_expect(
            page.get_by_label(f"Page {new_page_number}", exact=True).and_(page.locator(".selected"))
        ).to_be_visible(timeout=30_000)
        return True
