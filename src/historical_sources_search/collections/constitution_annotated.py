import logging
from typing import override
from urllib.parse import quote as url_escape

from playwright.async_api import Browser, Locator, Page, expect as pw_expect

from historical_sources_search.collections.base_browser_paging import CollectionBaseBrowserPaging
from historical_sources_search.exceptions import MissingInformationError, NavigationError
from historical_sources_search.search_result import CollectionInfo


class CollectionConstitutionAnnotated(CollectionBaseBrowserPaging):
    def __init__(self, browser: Browser):
        super().__init__(
            browser=browser,
            collection_info=CollectionInfo(
                name="Constitution Annotated",
                url="https://constitution.congress.gov/",
            ),
            logger=logging.getLogger(f"{__name__}.paging"),
        )

    @override
    async def _enter_query(self, page: Page, query: str):
        query_escaped = url_escape(query, safe="")
        search_url = f"https://constitution.congress.gov/search/{query_escaped}"
        response = await page.goto(search_url)
        if response is not None and not response.ok:
            raise NavigationError(f"Navigation to `{search_url}` failed with status {response.status}")

    @override
    def _get_locator_no_results(self, page: Page) -> Locator:
        return page.get_by_title("no-results")

    @override
    def _get_locator_result_by_index(self, page: Page, index: int) -> Locator:
        return page.locator("ul.search-results > li").nth(index)

    @override
    async def _get_result_url(self, page: Page, result_locator: Locator) -> str:
        item_title_link = result_locator.locator(".search-results-title").locator("a")
        item_title_href = await item_title_link.get_attribute("href")
        if not item_title_href:
            item_title_link_html = await item_title_link.inner_html()
            raise MissingInformationError(f"Search result did not have an href: {item_title_link_html}")
        return item_title_href

    @override
    async def _get_result_title(self, page: Page, result_locator: Locator) -> str:
        return await result_locator.locator(".search-results-title").inner_text()

    @override
    async def _get_result_detail(self, page: Page, result_locator: Locator) -> str | None:
        return await result_locator.locator(".search-results-summary").inner_text()

    @override
    async def _get_result_image_src(self, page: Page, result_locator: Locator) -> str | None:
        return None

    @override
    async def _advance_page(self, page: Page, current_page_index: int) -> bool:
        current_page_number = current_page_index + 1
        new_page_number = current_page_number + 1
        locator_pagination = page.locator(".search-results-control-pagination")
        next_page_button = locator_pagination.get_by_role("link", name=str(new_page_number), exact=True)
        try:
            await pw_expect(next_page_button).to_be_visible(timeout=1_000)
        except AssertionError:
            return False  # no more pages
        await next_page_button.click()
        await pw_expect(locator_pagination.locator(".pagination-item.active")).to_be_visible(timeout=30_000)
        return True
