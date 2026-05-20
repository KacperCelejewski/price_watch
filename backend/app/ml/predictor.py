import os
from typing import List, Optional
import numpy as np
import pandas as pd
import joblib
from loguru import logger
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from sklearn.linear_model import LinearRegression


MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


class PricePredictor:
    """
    Price predictor using either SimpleExpSmoothing (statsmodels) when enough
    seasonal data exists, or LinearRegression (scikit-learn) as a fallback.
    """

    MIN_SAMPLES_FOR_SES = 5

    def __init__(self) -> None:
        self._ses_model: Optional[object] = None
        self._lr_model: Optional[LinearRegression] = None
        self._use_ses: bool = False
        self._last_value: float = 0.0
        self._series_len: int = 0

    def fit(self, price_series: pd.Series) -> None:
        """Train the model on a price series (index = dates, values = prices)."""
        series = price_series.dropna()
        n = len(series)
        self._series_len = n

        if n < 2:
            logger.warning("Not enough data points to train predictor")
            self._last_value = float(series.iloc[-1]) if n == 1 else 0.0
            return

        self._last_value = float(series.iloc[-1])

        if n >= self.MIN_SAMPLES_FOR_SES:
            try:
                model = SimpleExpSmoothing(series.values.astype(float)).fit(
                    optimized=True, use_brute=True
                )
                self._ses_model = model
                self._use_ses = True
                logger.debug(f"PricePredictor: fitted SES on {n} samples")
                return
            except Exception as exc:
                logger.warning(f"SES fitting failed, falling back to LR: {exc}")

        # Linear regression fallback
        X = np.arange(n).reshape(-1, 1)
        y = series.values.astype(float)
        lr = LinearRegression()
        lr.fit(X, y)
        self._lr_model = lr
        self._use_ses = False
        logger.debug(f"PricePredictor: fitted LinearRegression on {n} samples")

    def predict(self, days: int) -> List[float]:
        """Return predicted prices for the next N days."""
        if days <= 0:
            return []

        if self._use_ses and self._ses_model is not None:
            try:
                forecast = self._ses_model.forecast(days)
                return [round(max(0.0, float(v)), 2) for v in forecast]
            except Exception as exc:
                logger.warning(f"SES prediction failed: {exc}")

        if self._lr_model is not None:
            base = self._series_len
            X_future = np.arange(base, base + days).reshape(-1, 1)
            preds = self._lr_model.predict(X_future)
            return [round(max(0.0, float(v)), 2) for v in preds]

        # Flat forecast using last known value
        return [round(self._last_value, 2)] * days

    def save_model(self, path: str) -> None:
        """Serialize the predictor to a joblib file."""
        joblib.dump(self, path)
        logger.info(f"Model saved to {path}")

    @classmethod
    def load_model(cls, path: str) -> "PricePredictor":
        """Load a predictor from a joblib file."""
        predictor = joblib.load(path)
        logger.info(f"Model loaded from {path}")
        return predictor

    @classmethod
    def model_path(cls, product_id: int) -> str:
        return os.path.join(MODELS_DIR, f"product_{product_id}.pkl")
