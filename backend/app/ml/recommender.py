from typing import Dict, Any, Optional
from loguru import logger
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.price import PriceHistory
from app.ml.data_processing import clean_price_series
from app.ml.predictor import PricePredictor


class ShoppingRecommender:
    """
    Provides shopping recommendations based on price history and predictions.

    Actions:
    - "buy"   — current price is at or below the predicted minimum → good time to buy
    - "wait"  — price is trending downward → a better deal is expected soon
    - "watch" — price is stable or uncertain → monitor and decide later
    """

    TREND_THRESHOLD_PCT = 3.0   # % decline to call a downward trend
    BUY_MARGIN_PCT = 2.0        # current price within 2% of predicted min → "buy"
    PREDICTION_DAYS = 14

    def should_buy_now(self, product_id: int, db: Session) -> Dict[str, Any]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return self._result("watch", 0.0, "Product not found", None, None)

        prices = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.scraped_at.asc())
            .all()
        )

        if not prices:
            return self._result("watch", 0.0, "No price history available", None, None)

        current_price = float(prices[-1].price)

        if len(prices) < 5:
            return self._result(
                "watch",
                0.3,
                "Insufficient price history — collecting more data",
                current_price,
                None,
            )

        df = clean_price_series(prices)
        if df.empty:
            return self._result("watch", 0.3, "No clean price data available", current_price, None)

        price_series = df.set_index("date")["price"] if "date" in df.columns else df["price"]

        predictor = PricePredictor()
        try:
            model_path = PricePredictor.model_path(product_id)
            predictor = PricePredictor.load_model(model_path)
        except Exception:
            predictor = PricePredictor()
            predictor.fit(price_series)

        predictions = predictor.predict(self.PREDICTION_DAYS)

        if not predictions:
            return self._result("watch", 0.3, "Could not generate predictions", current_price, None)

        predicted_min = min(predictions)
        days_to_min = predictions.index(predicted_min)

        # Determine trend from recent 7 days vs earlier
        recent = price_series.values[-7:] if len(price_series) >= 7 else price_series.values
        if len(recent) >= 2:
            trend_pct = (recent[-1] - recent[0]) / recent[0] * 100 if recent[0] > 0 else 0
        else:
            trend_pct = 0.0

        margin_pct = (current_price - predicted_min) / predicted_min * 100 if predicted_min > 0 else 0

        # Decision logic
        if margin_pct <= self.BUY_MARGIN_PCT:
            action = "buy"
            confidence = min(0.9, 0.6 + (self.BUY_MARGIN_PCT - margin_pct) / self.BUY_MARGIN_PCT * 0.3)
            reason = (
                f"Current price ({current_price:.2f} PLN) is at or near the predicted minimum "
                f"({predicted_min:.2f} PLN) — great time to buy."
            )
        elif trend_pct < -self.TREND_THRESHOLD_PCT:
            action = "wait"
            confidence = min(0.85, 0.5 + abs(trend_pct) / 20)
            reason = (
                f"Price has dropped {abs(trend_pct):.1f}% recently and is predicted to reach "
                f"{predicted_min:.2f} PLN in ~{days_to_min} days — consider waiting."
            )
        else:
            action = "watch"
            confidence = 0.5
            reason = (
                f"Price is stable. Predicted minimum over next {self.PREDICTION_DAYS} days: "
                f"{predicted_min:.2f} PLN (in ~{days_to_min} days)."
            )

        return self._result(action, round(confidence, 2), reason, predicted_min, days_to_min)

    @staticmethod
    def _result(
        action: str,
        confidence: float,
        reason: str,
        predicted_min_price: Optional[float],
        days_to_min: Optional[int],
    ) -> Dict[str, Any]:
        return {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "predicted_min_price": round(predicted_min_price, 2) if predicted_min_price is not None else None,
            "days_to_min": days_to_min,
        }
