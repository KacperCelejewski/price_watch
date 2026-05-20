"""
Pytest fixtures: in-memory SQLite test database, FastAPI test client, and seed data.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    return eng


@pytest.fixture(scope="session")
def tables(engine):
    # Override app database before importing models/app
    import app.database as db_module
    db_module.engine = engine
    db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from app.database import Base
    import app.models  # noqa: F401 — registers all models

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(engine, tables) -> Session:
    """Provide a transactional test DB session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db, tables) -> TestClient:
    """Provide a FastAPI test client wired to the test DB session."""
    from app.main import app
    from app.database import get_db

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_product(db) -> dict:
    """Create a product in the test DB and return it as a dict."""
    from app.models.product import Product

    product = Product(
        name="Test Product",
        url="https://example.com/product/1",
        shop="TestShop",
        category="Electronics",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"id": product.id, "name": product.name, "url": product.url}


@pytest.fixture
def seed_prices(db, seed_product) -> list:
    """Add 35 daily price records for the seed product."""
    from app.models.price import PriceHistory

    records = []
    base_price = 1000.0
    for i in range(35):
        record = PriceHistory(
            product_id=seed_product["id"],
            price=base_price + (i % 5) * 20 - 10,
            currency="PLN",
            scraped_at=datetime.utcnow() - timedelta(days=34 - i),
        )
        db.add(record)
        records.append(record)
    db.commit()
    return records
