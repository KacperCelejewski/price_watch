from typing import List, Dict, Any
import numpy as np
import pandas as pd
from loguru import logger


class AnomalyDetector:
    """
    Detect anomalous prices in a time series using Z-score method.

    Points where |z-score| > threshold are flagged as anomalies.
    IsolationForest is used as a secondary check when enough data is available.
    """

    Z_THRESHOLD = 2.5
    MIN_SAMPLES_FOR_ISO = 30

    def detect(self, price_series: pd.Series) -> List[Dict[str, Any]]:
        """
        Detect price anomalies.

        Parameters
        ----------
        price_series : pd.Series
            Index = dates (or integers), values = prices

        Returns
        -------
        list of dicts with keys: date, price, anomaly_type, severity
        """
        series = price_series.dropna()
        if len(series) < 4:
            logger.debug("AnomalyDetector: too few data points to detect anomalies")
            return []

        prices = series.values.astype(float)
        dates = [str(d)[:10] for d in series.index]

        anomalies: List[Dict[str, Any]] = []

        # Z-score detection
        mean = prices.mean()
        std = prices.std()

        if std == 0:
            return []

        z_scores = (prices - mean) / std

        for i, (date, price, z) in enumerate(zip(dates, prices, z_scores)):
            if abs(z) > self.Z_THRESHOLD:
                anomaly_type = "spike" if z > 0 else "drop"
                severity = round(min(float(abs(z)) / self.Z_THRESHOLD, 5.0), 2)
                anomalies.append(
                    {
                        "date": date,
                        "price": round(float(price), 2),
                        "anomaly_type": anomaly_type,
                        "severity": severity,
                        "z_score": round(float(z), 2),
                    }
                )

        # IsolationForest for larger datasets (supplements Z-score)
        if len(series) >= self.MIN_SAMPLES_FOR_ISO:
            try:
                from sklearn.ensemble import IsolationForest

                iso = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
                X = prices.reshape(-1, 1)
                labels = iso.fit_predict(X)
                scores = iso.decision_function(X)

                existing_dates = {a["date"] for a in anomalies}
                for i, (date, price, label, score) in enumerate(
                    zip(dates, prices, labels, scores)
                ):
                    if label == -1 and date not in existing_dates:
                        # IsolationForest anomaly not caught by Z-score
                        # Determine direction vs rolling median
                        window = prices[max(0, i - 5) : i + 1]
                        median = float(np.median(window))
                        anomaly_type = "spike" if price > median else "drop"
                        anomalies.append(
                            {
                                "date": date,
                                "price": round(float(price), 2),
                                "anomaly_type": anomaly_type,
                                "severity": round(float(abs(score)) * 2, 2),
                                "z_score": None,
                            }
                        )
            except ImportError:
                pass
            except Exception as exc:
                logger.warning(f"IsolationForest detection failed: {exc}")

        # Sort by date
        anomalies.sort(key=lambda x: x["date"])
        return anomalies
