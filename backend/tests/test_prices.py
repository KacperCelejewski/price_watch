"""Tests for price history and stats endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_price_history_empty(client: TestClient, seed_product: dict) -> None:
    response = client.get(f"/products/{seed_product['id']}/prices")
    assert response.status_code == 200
    assert response.json() == []


def test_price_history_with_data(client: TestClient, seed_product: dict, seed_prices: list) -> None:
    response = client.get(f"/products/{seed_product['id']}/prices", params={"days": 60})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 35
    # Should be ordered ascending by scraped_at
    dates = [p["scraped_at"] for p in data]
    assert dates == sorted(dates)


def test_price_history_pagination(client: TestClient, seed_product: dict, seed_prices: list) -> None:
    r1 = client.get(f"/products/{seed_product['id']}/prices", params={"limit": 10, "skip": 0, "days": 60})
    r2 = client.get(f"/products/{seed_product['id']}/prices", params={"limit": 10, "skip": 10, "days": 60})
    assert len(r1.json()) == 10
    assert len(r2.json()) == 10
    ids1 = {p["id"] for p in r1.json()}
    ids2 = {p["id"] for p in r2.json()}
    assert ids1.isdisjoint(ids2)


def test_price_history_not_found(client: TestClient) -> None:
    response = client.get("/products/9999/prices")
    assert response.status_code == 404


def test_price_stats(client: TestClient, seed_product: dict, seed_prices: list) -> None:
    response = client.get(f"/products/{seed_product['id']}/prices/stats", params={"days": 60})
    assert response.status_code == 200
    stats = response.json()
    assert stats["count"] == 35
    assert stats["min_price"] is not None
    assert stats["max_price"] is not None
    assert stats["avg_price"] is not None
    assert stats["min_price"] <= stats["avg_price"] <= stats["max_price"]
    assert stats["current_price"] is not None


def test_price_stats_days_filter(client: TestClient, seed_product: dict, seed_prices: list) -> None:
    # With days=7 we should get fewer records than with days=60
    r7 = client.get(f"/products/{seed_product['id']}/prices/stats", params={"days": 7})
    r60 = client.get(f"/products/{seed_product['id']}/prices/stats", params={"days": 60})
    assert r7.json()["count"] <= r60.json()["count"]


def test_price_stats_not_found(client: TestClient) -> None:
    response = client.get("/products/9999/prices/stats")
    assert response.status_code == 404
