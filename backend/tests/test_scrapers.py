"""Tests for GenericScraper with mocked httpx responses."""
import pytest
from unittest.mock import patch, MagicMock
import httpx


SAMPLE_HTML_WITH_ITEMPROP = """
<html>
<head><title>Test Product</title></head>
<body>
  <div class="product">
    <span itemprop="price" content="1299.99">1299.99 zł</span>
  </div>
</body>
</html>
"""

SAMPLE_HTML_WITH_CLASS_PRICE = """
<html>
<body>
  <div class="price">2 499,00 zł</div>
</body>
</html>
"""

SAMPLE_HTML_WITH_DATA_PRICE = """
<html>
<body>
  <div class="product" data-price="599.90">Some product</div>
</body>
</html>
"""

SAMPLE_HTML_NO_PRICE = """
<html>
<body>
  <div class="product">No price here</div>
</body>
</html>
"""

SAMPLE_HTML_CENEO = """
<html>
<body>
  <span class="product-offer__price">3 299,99 zł</span>
</body>
</html>
"""


def _make_response(html: str, status: int = 200) -> httpx.Response:
    return httpx.Response(status_code=status, text=html)


class TestGenericScraper:
    def _scrape_with_mock(self, html: str) -> object:
        from app.scrapers.generic import GenericScraper

        scraper = GenericScraper()
        with patch.object(scraper, "fetch_page", return_value=html):
            return scraper.scrape("https://example.com/product")

    def test_scrapes_itemprop_content(self) -> None:
        price = self._scrape_with_mock(SAMPLE_HTML_WITH_ITEMPROP)
        assert price == 1299.99

    def test_scrapes_class_price(self) -> None:
        price = self._scrape_with_mock(SAMPLE_HTML_WITH_CLASS_PRICE)
        assert price is not None
        assert price > 0

    def test_scrapes_data_price_attr(self) -> None:
        price = self._scrape_with_mock(SAMPLE_HTML_WITH_DATA_PRICE)
        assert price == 599.90

    def test_returns_none_when_no_price(self) -> None:
        price = self._scrape_with_mock(SAMPLE_HTML_NO_PRICE)
        assert price is None

    def test_returns_none_on_fetch_failure(self) -> None:
        from app.scrapers.generic import GenericScraper

        scraper = GenericScraper()
        with patch.object(scraper, "fetch_page", return_value=None):
            price = scraper.scrape("https://example.com/product")
        assert price is None


class TestCeneoScraper:
    def test_scrapes_product_offer_price(self) -> None:
        from app.scrapers.ceneo import CeneoScraper

        scraper = CeneoScraper()
        with patch.object(scraper, "fetch_page", return_value=SAMPLE_HTML_CENEO):
            price = scraper.scrape("https://ceneo.pl/product")
        assert price is not None
        assert price > 0


class TestBaseScraper:
    def test_parse_price_simple(self) -> None:
        from app.scrapers.generic import GenericScraper

        s = GenericScraper()
        assert s.parse_price("1299.99") == 1299.99

    def test_parse_price_polish_format(self) -> None:
        from app.scrapers.generic import GenericScraper

        s = GenericScraper()
        assert s.parse_price("1 299,99 zł") == 1299.99

    def test_parse_price_thousands_separator(self) -> None:
        from app.scrapers.generic import GenericScraper

        s = GenericScraper()
        assert s.parse_price("12 000,00") == 12000.00

    def test_parse_price_invalid(self) -> None:
        from app.scrapers.generic import GenericScraper

        s = GenericScraper()
        assert s.parse_price("no price here") is None

    def test_retry_logic(self) -> None:
        from app.scrapers.generic import GenericScraper

        scraper = GenericScraper()
        call_count = 0

        def flaky_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.RequestError("timeout", request=MagicMock())
            return _make_response("<html><body><span itemprop='price' content='99.99'>99</span></body></html>")

        with patch.object(scraper.client, "get", side_effect=flaky_get):
            with patch("time.sleep"):  # skip sleep delays in tests
                result = scraper.fetch_page("https://example.com")

        assert result is not None
        assert call_count == 3
