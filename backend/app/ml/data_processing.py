from typing import List, Dict, Any
import pandas as pd
import numpy as np
from loguru import logger


def clean_price_series(prices: list) -> pd.DataFrame:
    """
    Clean a list of PriceHistory ORM objects into a tidy daily DataFrame.

    Steps:
    1. Convert to DataFrame
    2. Remove outliers using IQR method
    3. Fill gaps via forward-fill then backward-fill
    4. Resample to daily frequency (last price of day)
    """
    if not prices:
        return pd.DataFrame(columns=["price"])

    records = [
        {"scraped_at": p.scraped_at, "price": float(p.price)}
        for p in prices
    ]
    df = pd.DataFrame(records)
    df["scraped_at"] = pd.to_datetime(df["scraped_at"], utc=True)
    df = df.sort_values("scraped_at").set_index("scraped_at")

    # Remove duplicates — keep last in same timestamp
    df = df[~df.index.duplicated(keep="last")]

    # IQR-based outlier removal
    if len(df) >= 4:
        q1 = df["price"].quantile(0.25)
        q3 = df["price"].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 2.5 * iqr
        upper = q3 + 2.5 * iqr
        mask = (df["price"] >= lower) & (df["price"] <= upper)
        removed = (~mask).sum()
        if removed > 0:
            logger.debug(f"IQR outlier removal: dropped {removed} records")
        df = df[mask]

    if df.empty:
        return df

    # Resample to daily — take last observation each day
    daily = df["price"].resample("D").last()

    # Fill gaps (weekends, no scrape days)
    daily = daily.ffill().bfill()

    return daily.reset_index().rename(columns={"scraped_at": "date"})


def aggregate_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute summary statistics from a cleaned price DataFrame."""
    if df.empty or "price" not in df.columns:
        return {
            "min": None,
            "max": None,
            "avg": None,
            "median": None,
            "std": None,
            "count": 0,
        }
    series = df["price"].dropna()
    return {
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "avg": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
        "count": int(len(series)),
    }


def detect_price_drops(df: pd.DataFrame, threshold_pct: float = 5.0) -> List[Dict[str, Any]]:
    """
    Detect price drop events in a daily price DataFrame.

    A drop event is when the price falls by >= threshold_pct% compared to the previous day.
    Returns a list of dicts: {date, price, prev_price, drop_pct}
    """
    if df.empty or "price" not in df.columns or len(df) < 2:
        return []

    events = []
    prices = df["price"].values
    dates = df["date"].values if "date" in df.columns else df.index.values

    for i in range(1, len(prices)):
        prev = prices[i - 1]
        curr = prices[i]
        if prev > 0 and curr < prev:
            drop_pct = (prev - curr) / prev * 100
            if drop_pct >= threshold_pct:
                events.append(
                    {
                        "date": str(dates[i])[:10],
                        "price": round(float(curr), 2),
                        "prev_price": round(float(prev), 2),
                        "drop_pct": round(drop_pct, 2),
                    }
                )
    return events
