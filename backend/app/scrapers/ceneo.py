from typing import Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.base import BaseScraper


class CeneoScraper(BaseScraper):
    """Scraper for ceneo.pl product pages."""

    PRICE_SELECTORS = [
        ".product-offer__price",
        ".price-box",
        ".product-price",
        "[class*='price']",
        ".js_productsBox-price",
        ".price",
    ]

    def scrape(self, url: str) -> Optional[float]:
        html = self.fetch_page(url)
        if html is None:
            return None

        soup = BeautifulSoup(html, "html.parser")

        for selector in self.PRICE_SELECTORS:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    price = self.parse_price(text)
                    if price is not None and price > 0:
                        logger.debug(f"Ceneo scraped price {price} from {url} (selector: {selector})")
                        return price

        # Fallback: look for data-price attribute
        element = soup.find(attrs={"data-price": True})
        if element:
            raw = element.get("data-price", "")
            price = self.parse_price(str(raw))
            if price is not None and price > 0:
                return price

        logger.warning(f"CeneoScraper: could not find price on {url}")
        return None
