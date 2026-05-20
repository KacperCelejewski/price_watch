from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.logging import setup_logging
from app.routers import products, prices, alerts, scraper
from app.routers import predictions, recommendations, logs
from app.scrapers.scheduler import start_scheduler, stop_scheduler

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Price Watch API")
    start_scheduler()
    yield
    logger.info("Shutting down Price Watch API")
    stop_scheduler()


app = FastAPI(
    title="Price Watch API",
    description="Track product prices, predict trends, and get shopping recommendations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(prices.router)
app.include_router(alerts.router)
app.include_router(scraper.router)
app.include_router(predictions.router)
app.include_router(recommendations.router)
app.include_router(logs.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
