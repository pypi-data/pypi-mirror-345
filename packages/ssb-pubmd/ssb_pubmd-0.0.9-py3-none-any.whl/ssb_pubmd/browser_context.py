from typing import cast

from playwright.async_api import BrowserContext
from playwright.async_api import async_playwright

from .notebook_syncer import Response


class BrowserRequestContext:
    """Creates a logged in browser context from which to send requests."""

    def __init__(self) -> None:
        """Initializes a browser context with a login url."""
        self._storage_state_path: str = "browser_context.json"
        self._context: BrowserContext | None = None

    async def create_new(self, login_url: str) -> BrowserContext:
        """Creates a browser context by opening a logging page and waiting for it to be closed by user."""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)

        self._context = await browser.new_context()
        login_page = await self._context.new_page()

        await login_page.goto(login_url)
        await login_page.wait_for_event("close", timeout=0)

        await self._context.storage_state(path=self._storage_state_path)

        return self._context

    async def recreate_from_file(self) -> BrowserContext:
        """Restores a browser context from the storage state file."""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)

        self._context = await browser.new_context(
            storage_state=self._storage_state_path
        )

        return self._context

    async def send_request(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
    ) -> Response:
        """Sends a request tp the specified url, optionally with headers and data, within the browser context."""
        if self._context is None:
            raise ValueError("Browser context has not been created.")

        params = cast(dict[str, str | float | bool], data)
        api_response = await self._context.request.post(
            url,
            params=params,
        )

        try:
            body = await api_response.json()
            body = dict(body)
        except Exception:
            body = None

        response = Response(
            status_code=api_response.status,
            body=body,
        )

        return response
