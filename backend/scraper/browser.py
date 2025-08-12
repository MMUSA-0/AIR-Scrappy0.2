from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .anti_bot import build_context_kwargs, enable_request_blocking, jitter_delay


class BrowserManager:
    _instance: "BrowserManager | None" = None

    def __init__(self, max_contexts: int = 3) -> None:
        self._playwright = None
        self._browser: Browser | None = None
        self._sem = asyncio.Semaphore(max_contexts)
        self._lock = asyncio.Lock()

    @classmethod
    def instance(cls) -> "BrowserManager":
        if cls._instance is None:
            cls._instance = BrowserManager()
        return cls._instance

    async def start(self) -> None:
        async with self._lock:
            if self._browser:
                return
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)

    async def stop(self) -> None:
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None

    @asynccontextmanager
    async def context(self) -> AsyncIterator[BrowserContext]:
        if self._browser is None:
            await self.start()
        assert self._browser is not None
        await self._sem.acquire()
        try:
            ctx = await self._browser.new_context(**build_context_kwargs())
            try:
                yield ctx
            finally:
                await ctx.close()
        finally:
            self._sem.release()

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        async with self.context() as ctx:
            page = await ctx.new_page()
            await enable_request_blocking(page)
            yield page


async def render_and_get_next_data(url: str, timeout_s: int = 15) -> str | None:
    mgr = BrowserManager.instance()
    await mgr.start()
    async with mgr.page() as page:
        await jitter_delay()
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_s * 1000)
        # Wait for __NEXT_DATA__ script if present
        try:
            handle = await page.wait_for_selector('script#__NEXT_DATA__', timeout=timeout_s * 1000)
            content = await handle.inner_text()
            return content
        except Exception:
            return None


async def render_and_get_html(url: str, timeout_s: int = 15) -> str:
    mgr = BrowserManager.instance()
    await mgr.start()
    async with mgr.page() as page:
        await jitter_delay()
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_s * 1000)
        return await page.content()
