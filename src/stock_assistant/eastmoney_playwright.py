from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

from .eastmoney import EASTMONEY_KLINE_URL, bars_from_eastmoney_json, eastmoney_kline_params
from .models import DailyBar


class EastmoneyPlaywrightProvider:
    """Use a real installed browser via Playwright to fetch Eastmoney JSON."""

    def __init__(
        self,
        timeout_ms: int = 30_000,
        headless: bool = True,
        executable_path: str = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        user_data_dir: str | None = None,
    ):
        self.timeout_ms = timeout_ms
        self.headless = headless
        self.executable_path = executable_path
        self.user_data_dir = user_data_dir or os.environ.get("EASTMONEY_CHROME_USER_DATA_DIR")

    def stock_codes(self) -> list[str]:
        return []

    def history(self, code: str, start: date | None = None, end: date | None = None) -> list[DailyBar]:
        params = eastmoney_kline_params(code, start, end)
        query = "&".join(f"{key}={value}" for key, value in params.items())
        url = f"{EASTMONEY_KLINE_URL}?{query}"
        payload = self.fetch_json(url)
        return bars_from_eastmoney_json(payload)

    def fetch_json(self, url: str) -> dict:
        with sync_playwright() as p:
            if self.user_data_dir:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(Path(self.user_data_dir).expanduser()),
                    headless=self.headless,
                    executable_path=self.executable_path,
                    args=["--disable-blink-features=AutomationControlled"],
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    extra_http_headers={
                        "Referer": "https://quote.eastmoney.com/",
                        "Accept": "application/json,text/plain,*/*",
                    },
                )
                try:
                    page = context.new_page()
                    return self._goto_and_parse(page, url)
                finally:
                    context.close()

            browser = p.chromium.launch(
                headless=self.headless,
                executable_path=self.executable_path,
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    extra_http_headers={
                        "Referer": "https://quote.eastmoney.com/",
                        "Accept": "application/json,text/plain,*/*",
                    },
                )
                page = context.new_page()
                return self._goto_and_parse(page, url)
            finally:
                browser.close()

    def _goto_and_parse(self, page, url: str) -> dict:
        response = page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
        if response is None:
            raise RuntimeError("Playwright page.goto returned no response")
        text = page.locator("body").inner_text(timeout=self.timeout_ms).strip()
        if not text:
            text = page.content()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Playwright got non-json response: {text[:300]}") from exc
