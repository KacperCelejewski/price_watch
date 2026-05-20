"""Tests for GET/POST /products endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_list_products_empty(client: TestClient) -> None:
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product(client: TestClient) -> None:
    payload = {
        "name": "iPhone 15",
        "url": "https://ceneo.pl/iphone-15",
        "shop": "Ceneo",
        "category": "Electronics",
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "iPhone 15"
    assert data["id"] > 0
    assert data["shop"] == "Ceneo"


def test_create_product_duplicate_url(client: TestClient) -> None:
    payload = {
        "name": "Product A",
        "url": "https://ceneo.pl/duplicate",
    }
    r1 = client.post("/products", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/products", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"]


def test_get_product_not_found(client: TestClient) -> None:
    response = client.get("/products/9999")
    assert response.status_code == 404


def test_get_product_by_id(client: TestClient, seed_product: dict) -> None:
    response = client.get(f"/products/{seed_product['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == seed_product["id"]
    assert data["name"] == seed_product["name"]
    assert "prices" in data


def test_search_products_by_name(client: TestClient) -> None:
    client.post("/products", json={"name": "Samsung TV 65", "url": "https://example.com/tv"})
    client.post("/products", json={"name": "Apple Watch", "url": "https://example.com/watch"})

    response = client.get("/products", params={"name": "samsung"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert all("samsung" in r["name"].lower() for r in results)


def test_search_products_by_category(client: TestClient) -> None:
    client.post(
        "/products",
        json={"name": "Laptop X", "url": "https://example.com/laptop", "category": "Laptops"},
    )
    response = client.get("/products", params={"category": "Laptops"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert all(r["category"] == "Laptops" for r in results)


def test_delete_product(client: TestClient, seed_product: dict) -> None:
    response = client.delete(f"/products/{seed_product['id']}")
    assert response.status_code == 204

    response = client.get(f"/products/{seed_product['id']}")
    assert response.status_code == 404


def test_pagination(client: TestClient) -> None:
    for i in range(5):
        client.post(
            "/products",
            json={"name": f"Paginated Product {i}", "url": f"https://example.com/page/{i}"},
        )
    r1 = client.get("/products", params={"limit": 2, "skip": 0})
    r2 = client.get("/products", params={"limit": 2, "skip": 2})
    assert len(r1.json()) == 2
    ids1 = {p["id"] for p in r1.json()}
    ids2 = {p["id"] for p in r2.json()}
    assert ids1.isdisjoint(ids2)
