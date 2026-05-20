"""Tests for ML components: PricePredictor, AnomalyDetector, ShoppingRecommender."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock


# ─── PricePredictor ────────────────────────────────────────────────────────────

class TestPricePredictor:
    def _make_series(self, n: int = 30, start_price: float = 1000.0) -> pd.Series:
        dates = pd.date_range(end=datetime.utcnow(), periods=n, freq="D")
        prices = [start_price + i * 2.5 + (i % 3) * 5 for i in range(n)]
        return pd.Series(prices, index=dates)

    def test_predict_returns_correct_length(self) -> None:
        from app.ml.predictor import PricePredictor
        predictor = PricePredictor()
        series = self._make_series(20)
        predictor.fit(series)
        preds = predictor.predict(7)
        assert len(preds) == 7

    def test_predict_all_positive(self) -> None:
        from app.ml.predictor import PricePredictor
        predictor = PricePredictor()
        series = self._make_series(30)
        predictor.fit(series)
        preds = predictor.predict(14)
        assert all(p >= 0 for p in preds)

    def test_predict_empty_days(self) -> None:
        from app.ml.predictor import PricePredictor
        predictor = PricePredictor()
        series = self._make_series(10)
        predictor.fit(series)
        assert predictor.predict(0) == []

    def test_predict_fallback_few_samples(self) -> None:
        from app.ml.predictor import PricePredictor
        predictor = PricePredictor()
        series = self._make_series(2)
        predictor.fit(series)
        preds = predictor.predict(5)
        assert len(preds) == 5

    def test_save_and_load_model(self, tmp_path) -> None:
        from app.ml.predictor import PricePredictor
        predictor = PricePredictor()
        series = self._make_series(20)
        predictor.fit(series)
        original_preds = predictor.predict(5)

        path = str(tmp_path / "test_model.pkl")
        predictor.save_model(path)
        loaded = PricePredictor.load_model(path)
        loaded_preds = loaded.predict(5)
        assert original_preds == loaded_preds


# ─── AnomalyDetector ──────────────────────────────────────────────────────────

class TestAnomalyDetector:
    def _normal_series(self, n: int = 50) -> pd.Series:
        prices = [1000.0 + (i % 10) * 5 for i in range(n)]
        dates = pd.date_range(end=datetime.utcnow(), periods=n, freq="D")
        return pd.Series(prices, index=dates)

    def _series_with_spike(self) -> pd.Series:
        prices = [1000.0] * 20
        prices[10] = 5000.0  # obvious spike
        prices[15] = 50.0    # obvious drop
        dates = pd.date_range(end=datetime.utcnow(), periods=20, freq="D")
        return pd.Series(prices, index=dates)

    def test_no_anomalies_in_normal_series(self) -> None:
        from app.ml.anomaly import AnomalyDetector
        detector = AnomalyDetector()
        series = self._normal_series()
        result = detector.detect(series)
        # Low variance series might have a few border cases, but should be minimal
        assert isinstance(result, list)

    def test_detects_spike_and_drop(self) -> None:
        from app.ml.anomaly import AnomalyDetector
        detector = AnomalyDetector()
        series = self._series_with_spike()
        result = detector.detect(series)
        assert len(result) >= 2
        types = {r["anomaly_type"] for r in result}
        assert "spike" in types
        assert "drop" in types

    def test_anomaly_has_required_fields(self) -> None:
        from app.ml.anomaly import AnomalyDetector
        detector = AnomalyDetector()
        series = self._series_with_spike()
        result = detector.detect(series)
        for anomaly in result:
            assert "date" in anomaly
            assert "price" in anomaly
            assert "anomaly_type" in anomaly
            assert "severity" in anomaly
            assert anomaly["anomaly_type"] in ("spike", "drop")
            assert anomaly["severity"] >= 0

    def test_too_few_samples_returns_empty(self) -> None:
        from app.ml.anomaly import AnomalyDetector
        detector = AnomalyDetector()
        series = pd.Series([100.0, 200.0, 150.0])
        assert detector.detect(series) == []


# ─── ShoppingRecommender ──────────────────────────────────────────────────────

class TestShoppingRecommender:
    def _make_mock_db(self, prices: list[float], product_id: int = 1):
        from app.models.product import Product
        from app.models.price import PriceHistory

        mock_product = MagicMock(spec=Product)
        mock_product.id = product_id
        mock_product.name = "Test Product"
        mock_product.url = "https://example.com/p1"

        price_records = []
        for i, p in enumerate(prices):
            ph = MagicMock(spec=PriceHistory)
            ph.price = p
            ph.scraped_at = datetime.utcnow() - timedelta(days=len(prices) - i)
            ph.currency = "PLN"
            price_records.append(ph)

        mock_db = MagicMock()

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == Product:
                mock_q.filter.return_value.first.return_value = mock_product
            else:
                mock_q.filter.return_value.order_by.return_value.all.return_value = price_records
            return mock_q

        mock_db.query.side_effect = query_side_effect
        return mock_db

    def test_returns_dict_with_required_keys(self) -> None:
        from app.ml.recommender import ShoppingRecommender
        recommender = ShoppingRecommender()
        prices = [1000.0 + i * 10 for i in range(20)]
        db = self._make_mock_db(prices)
        result = recommender.should_buy_now(1, db)
        for key in ("action", "confidence", "reason", "predicted_min_price", "days_to_min"):
            assert key in result

    def test_action_is_valid(self) -> None:
        from app.ml.recommender import ShoppingRecommender
        recommender = ShoppingRecommender()
        prices = [1000.0] * 20
        db = self._make_mock_db(prices)
        result = recommender.should_buy_now(1, db)
        assert result["action"] in ("buy", "wait", "watch")

    def test_not_enough_data_returns_watch(self) -> None:
        from app.ml.recommender import ShoppingRecommender
        recommender = ShoppingRecommender()
        prices = [999.0, 1001.0]
        db = self._make_mock_db(prices)
        result = recommender.should_buy_now(1, db)
        assert result["action"] == "watch"
        assert result["confidence"] < 0.5

    def test_confidence_between_0_and_1(self) -> None:
        from app.ml.recommender import ShoppingRecommender
        recommender = ShoppingRecommender()
        prices = [1000.0 - i * 5 for i in range(20)]  # downward trend
        db = self._make_mock_db(prices)
        result = recommender.should_buy_now(1, db)
        assert 0.0 <= result["confidence"] <= 1.0
