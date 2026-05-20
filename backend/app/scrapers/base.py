import re
import time
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from loguru import logger


class BaseScraper(ABC):
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0

    def __init__(self) -> None:
        self.client = httpx.Client(
            headers=self.HEADERS,
            follow_redirects=True,
            timeout=30.0,
        )

    @abstractmethod
    def scrape(self, url: str) -> Optional[float]:
        """Scrape price from the given URL. Returns price as float or None."""
        ...

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content with retry logic."""
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    f"HTTP {exc.response.status_code} fetching {url} (attempt {attempt}/{self.MAX_RETRIES})"
                )
                last_exc = exc
            except httpx.RequestError as exc:
                logger.warning(
                    f"Request error fetching {url} (attempt {attempt}/{self.MAX_RETRIES}): {exc}"
                )
                last_exc = exc
            if attempt < self.MAX_RETRIES:
                time.sleep(self.RETRY_DELAY * attempt)
        logger.error(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts: {last_exc}")
        return None

    def parse_price(self, raw: str) -> Optional[float]:
        """Parse a price string like '1 299,99 zł' or '1299.99' to float."""
        cleaned = re.sub(r"[^\d,.]", "", raw.replace("\xa0", "").replace(" ", ""))
        cleaned = cleaned.replace(",", ".")
        # Remove extra dots (thousands separators)
        parts = cleaned.split(".")
        if len(parts) > 2:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        try:
            return float(cleaned)
        except ValueError:
            return None

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "BaseScraper":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
