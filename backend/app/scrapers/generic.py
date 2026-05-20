from typing import Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.base import BaseScraper


class GenericScraper(BaseScraper):
    """Generic price scraper that tries common CSS selectors."""

    PRICE_SELECTORS = [
        "[itemprop='price']",
        "[data-price]",
        ".price",
        ".product-price",
        ".offer-price",
        ".sale-price",
        "#price",
        "[class*='price']",
        "[id*='price']",
    ]

    def scrape(self, url: str) -> Optional[float]:
        html = self.fetch_page(url)
        if html is None:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Try meta og:price or product:price
        for prop in ["product:price:amount", "og:price:amount"]:
            meta = soup.find("meta", property=prop)
            if meta:
                content = meta.get("content", "")
                price = self.parse_price(str(content))
                if price is not None and price > 0:
                    return price

        # Try itemprop="price" with content attribute
        elem = soup.find(attrs={"itemprop": "price"})
        if elem:
            content = elem.get("content") or elem.get("data-price")
            if content:
                price = self.parse_price(str(content))
                if price is not None and price > 0:
                    return price
            text = elem.get_text(strip=True)
            price = self.parse_price(text)
            if price is not None and price > 0:
                return price

        # Try data-price attribute anywhere
        elem = soup.find(attrs={"data-price": True})
        if elem:
            raw = elem.get("data-price", "")
            price = self.parse_price(str(raw))
            if price is not None and price > 0:
                return price

        for selector in self.PRICE_SELECTORS:
            elements = soup.select(selector)
            for element in elements:
                content = element.get("content") or element.get("data-price")
                if content:
                    price = self.parse_price(str(content))
                    if price is not None and price > 0:
                        return price
                text = element.get_text(strip=True)
                if text:
                    price = self.parse_price(text)
                    if price is not None and price > 0:
                        logger.debug(f"GenericScraper scraped price {price} from {url}")
                        return price

        logger.warning(f"GenericScraper: could not find price on {url}")
        return None
