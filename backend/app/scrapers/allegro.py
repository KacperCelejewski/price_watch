from typing import Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.base import BaseScraper


class AllegroScraper(BaseScraper):
    """Scraper for allegro.pl offer pages."""

    PRICE_SELECTORS = [
        "[data-testid='price-value']",
        "[data-role='price']",
        ".price",
        ".m-price",
        "[class*='price']",
        "[itemprop='price']",
        "[data-analytics-value]",
    ]

    def scrape(self, url: str) -> Optional[float]:
        html = self.fetch_page(url)
        if html is None:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Try meta tag first (reliable for Allegro)
        meta = soup.find("meta", {"itemprop": "price"})
        if meta:
            content = meta.get("content", "")
            price = self.parse_price(str(content))
            if price is not None and price > 0:
                logger.debug(f"Allegro scraped price {price} from meta tag on {url}")
                return price

        for selector in self.PRICE_SELECTORS:
            elements = soup.select(selector)
            for element in elements:
                # Check content attribute first
                content = element.get("content") or element.get("data-analytics-value")
                if content:
                    price = self.parse_price(str(content))
                    if price is not None and price > 0:
                        logger.debug(f"Allegro scraped price {price} from {url} (attr, selector: {selector})")
                        return price

                text = element.get_text(strip=True)
                if text:
                    price = self.parse_price(text)
                    if price is not None and price > 0:
                        logger.debug(f"Allegro scraped price {price} from {url} (selector: {selector})")
                        return price

        logger.warning(f"AllegroScraper: could not find price on {url}")
        return None
