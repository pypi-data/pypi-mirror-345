from __future__ import annotations

import asyncio
from collections.abc import Iterable
from contextlib import suppress
from enum import StrEnum
from http import HTTPStatus
from typing import Any

import backoff
import httpx
import truststore
from html2text import HTML2Text

with suppress(ImportError):
    from playwright.async_api import Browser, async_playwright, expect
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .cleanup import cleanup_page

truststore.inject_into_ssl()

MAX_TRIES: int = 3
MAX_TIMEOUT: int = 60
REQUEST_TIMEOUT: int = 10
# In milliseconds
PRE_ACTION_TIMEOUT: int = 10 * 1_000


class PageElementAction(StrEnum):
    CLICK = "click"
    TO_BE_VISIBLE = "to_be_visible"


async def __download_via_request(
    page_url: str,
    *,
    user_agent: str | None = None,
) -> str | None:
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            page_url,
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers=(
                {
                    "User-Agent": user_agent,
                } if user_agent
                else {}
            ),
        )

    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        # It also triggers backoff if necessary
        return None

    response.raise_for_status()

    return response.text


async def __download_via_browser(
    page_url: str,
    *,
    user_agent: str | None = None,
    pre_actions: Iterable[tuple[str, PageElementAction]] | None = None,
) -> str | None:
    async with async_playwright() as playwright:
        browser: Browser = await playwright.chromium.launch()
        await browser.new_context(
            user_agent=user_agent,
        )

        page = await browser.new_page()
        response = await page.goto(page_url)
        if not response:
            return None
        if response.status == HTTPStatus.TOO_MANY_REQUESTS:
            # It also triggers backoff if necessary
            return None

        for selector, action in pre_actions or []:
            with suppress(AssertionError, PlaywrightTimeoutError):
                match action:
                    case PageElementAction.CLICK:
                        await page.locator(selector).click(
                            timeout=PRE_ACTION_TIMEOUT,
                            # Allow click even current element is covered by other elements.
                            # Otherwise, other pre-actions are needed before this pre-action
                            # to dismiss those covering elements.
                            # However, it is possible that dismissing those covering elements
                            # is necessary logic for page to function properly.
                            force=True,
                        )
                    case PageElementAction.TO_BE_VISIBLE:
                        await expect(page.locator(selector)).to_be_visible(
                            timeout=PRE_ACTION_TIMEOUT,
                        )

        html: str = await page.content()

        await browser.close()

    return html


@backoff.on_predicate(
    backoff.expo,
    max_tries=MAX_TRIES,
    max_time=MAX_TIMEOUT,
)
async def download_page_async(
    page_url: str,
    *,
    cleanup: bool = False,
    text_only: bool = False,
    user_agent: str | None = None,
    use_browser: bool = False,
    pre_actions: Iterable[tuple[str, PageElementAction]] | None = None,
) -> str | None:
    page_html: str | None
    if use_browser:
        page_html = await __download_via_browser(
            page_url,
            user_agent=user_agent,
            pre_actions=pre_actions,
        )
    else:
        page_html = await __download_via_request(
            page_url,
            user_agent=user_agent,
        )
    if page_html is None:
        return None

    if cleanup:
        page_html = await cleanup_page(page_html)

    if text_only:
        h = HTML2Text()
        h.ignore_images = True
        h.ignore_links = True
        return h.handle(page_html)

    return page_html


def download_page(
    image_url: str,
    **kwargs: Any,
) -> str | None:
    return asyncio.run(download_page_async(
        image_url,
        **kwargs,
    ))
