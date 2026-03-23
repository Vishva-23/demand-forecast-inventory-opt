"""
forecast.py
===========
Probabilistic Demand Forecasting across product/location hierarchies.

Models implemented:
  1. Exponential Smoothing (Holt-Winters) — baseline heuristic
  2. Bayesian Structural Time Series (via Prophet) — probabilistic
  3. Quantile Regression (LightGBM) — ML-based prediction intervals

Each model produces point forecasts + prediction intervals (P10, P50, P90).
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional

# ── Forecast result container ──────────────────────────────────
@dataclass
class ForecastResult:
    sku: str
    warehouse: str
    model_name: str
    dates: List
    actuals: np.ndarray           # historical demand
    point_forecast: np.ndarray    # P50
    lower_bound: np.ndarray       # P10
    upper_bound: np.ndarray       # P90
    mape: float
    rmse: float
    coverage: float               # % of actuals within [P10, P90]

    def to_dataframe(self) -> pd.DataFrame:
        n_hist = len(self.actuals)
        n_fc = len(self.point_forecast)
        rows = []
        for i in range(n_fc):
            rows.append({
                "date": self.dates[i] if i < len(self.dates) else None,
                "sku": self.sku,
                "warehouse": self.warehouse,
                "model": self.model_name,
                "actual": self.actuals[i] if i < n_hist else None,
                "forecast_p50": self.point_forecast[i],
                "forecast_p10": self.lower_bound[i],
                "forecast_p90": self.upper_bound[i],
            })
        return pd.DataFrame(rows)


# ── Evaluation metrics ─────────────────────────────────────────
def _mape(actual, predicted):
    mask = actual > 0
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)

def _rmse(actual, predicted):
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))

def _coverage(actual, lower, upper):
    within = ((actual >= lower) & (actual <= upper)).sum()
    return float(within / len(actual) * 100) if len(actual) > 0 else 0.0


# ── Model 1: Holt-Winters Exponential Smoothing ───────────────
class HoltWintersForecaster:
    """Triple exponential smoothing with multiplicative seasonality."""

    def __init__(self, season_length: int = 52):
        self.season_length = season_length

    def fit_predict(
        self,
        series: np.ndarray,
        horizon: int = 12,
        alpha: float = 0.3,
        beta: float = 0.05,
        gamma: float = 0.15,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        n = len(series)
        sl = self.season_length

        # Initialization
        level = np.mean(series[:sl])
        trend = (np.mean(series[sl:2*sl]) - np.mean(series[:sl])) / sl if n >= 2*sl else 0
        seasonal = np.zeros(n + horizon)
        for i in range(sl):
            seasonal[i] = series[i] / level if level > 0 else 1.0

        levels = np.zeros(n)
        trends = np.zeros(n)
        fitted = np.zeros(n)
        residuals = np.zeros(n)

        # Fit
        for t in range(n):
            if t < sl:
                levels[t] = level
                trends[t] = trend
                fitted[t] = (level + trend) * seasonal[t]
                residuals[t] = series[t] - fitted[t]
                continue

            prev_level = levels[t-1]
            prev_trend = trends[t-1]
            prev_seasonal = seasonal[t - sl]

            levels[t] = alpha * (series[t] / max(prev_seasonal, 0.01)) + (1 - alpha) * (prev_level + prev_trend)
            trends[t] = beta * (levels[t] - prev_level) + (1 - beta) * prev_trend
            seasonal[t] = gamma * (series[t] / max(levels[t], 0.01)) + (1 - gamma) * prev_seasonal

            fitted[t] = (levels[t] + trends[t]) * seasonal[t]
            residuals[t] = series[t] - fitted[t]

        # Forecast
        last_level = levels[-1]
        last_trend = trends[-1]
        forecast = np.zeros(horizon)
        for h in range(horizon):
            s_idx = n - sl + (h % sl)
            forecast[h] = (last_level + (h + 1) * last_trend) * seasonal[max(s_idx, 0)]
            forecast[h] = max(0, forecast[h])

        # Prediction intervals from residual std
        residual_std = np.std(residuals[sl:]) if n > sl else np.std(residuals)
        widening = np.sqrt(np.arange(1, horizon + 1))
        lower = np.maximum(0, forecast - 1.28 * residual_std * widening)  # P10
        upper = forecast + 1.28 * residual_std * widening                  # P90

        return forecast, lower, upper


# ── Model 2: Bayesian / Prophet-style decomposition ───────────
class BayesianForecaster:
    """
    Simplified Bayesian structural time series.
    Decomposes into trend + seasonality + residual with MCMC-like sampling
    for uncertainty quantification.
    """

    def __init__(self, season_length: int = 52, n_samples: int = 200):
        self.season_length = season_length
        self.n_samples = n_samples

    def fit_predict(
        self, series: np.ndarray, horizon: int = 12
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        n = len(series)
        sl = self.season_length
        t = np.arange(n)

        # Trend estimation (robust linear)
        z = np.polyfit(t, series, 1)
        trend = np.polyval(z, t)
        detrended = series - trend

        # Seasonal estimation (periodic averaging)
        seasonal = np.zeros(n)
        for i in range(sl):
            indices = np.arange(i, n, sl)
            seasonal[indices] = np.mean(detrended[indices])

        residual = series - trend - seasonal
        res_std = np.std(residual)

        # Generate future trend
        future_t = np.arange(n, n + horizon)
        future_trend = np.polyval(z, future_t)
        future_seasonal = np.array([seasonal[(n + h) % sl] for h in range(horizon)])

        # Monte Carlo sampling for prediction intervals
        samples = np.zeros((self.n_samples, horizon))
        for s in range(self.n_samples):
            # Add uncertainty to trend slope
            slope_noise = np.random.normal(0, abs(z[0]) * 0.1)
            noisy_trend = future_trend + slope_noise * np.arange(1, horizon + 1)
            # Add residual noise (widening)
            noise = np.random.normal(0, res_std * np.sqrt(np.arange(1, horizon + 1)))
            samples[s] = np.maximum(0, noisy_trend + future_seasonal + noise)

        forecast = np.percentile(samples, 50, axis=0)
        lower = np.percentile(samples, 10, axis=0)
        upper = np.percentile(samples, 90, axis=0)

        return forecast, lower, upper


# ── Model 3: Quantile Regression (feature-based) ──────────────
class QuantileForecaster:
    """
    Feature-engineered quantile forecaster using gradient boosting.
    Falls back to a simpler method if LightGBM is unavailable.
    """

    def __init__(self, season_length: int = 52):
        self.season_length = season_length

    def _build_features(self, series: np.ndarray) -> pd.DataFrame:
        n = len(series)
        sl = self.season_length
        df = pd.DataFrame({"y": series, "t": np.arange(n)})
        df["week_of_year"] = df["t"] % sl
        df["sin_annual"] = np.sin(2 * np.pi * df["t"] / sl)
        df["cos_annual"] = np.cos(2 * np.pi * df["t"] / sl)

        # Lag features
        for lag in [1, 2, 4, 13, 26, 52]:
            df[f"lag_{lag}"] = df["y"].shift(lag)

        # Rolling stats
        for w in [4, 13, 26]:
            df[f"roll_mean_{w}"] = df["y"].rolling(w).mean()
            df[f"roll_std_{w}"] = df["y"].rolling(w).std()

        return df

    def fit_predict(
        self, series: np.ndarray, horizon: int = 12
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        df = self._build_features(series)
        df = df.dropna()

        feature_cols = [c for c in df.columns if c not in ["y"]]
        X = df[feature_cols].values
        y = df["y"].values

        # Train/val split
        split = int(len(X) * 0.8)
        X_train, y_train = X[:split], y[:split]
        X_val, y_val = X[split:], y[split:]

        try:
            import lightgbm as lgb

            forecasts = {}
            for quantile, label in [(0.1, "p10"), (0.5, "p50"), (0.9, "p90")]:
                model = lgb.LGBMRegressor(
                    objective="quantile",
                    alpha=quantile,
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=6,
                    verbose=-1,
                )
                model.fit(X_train, y_train)
                forecasts[label] = model.predict(X_val)

            # Use last known features for future (recursive simplified)
            last_features = X[-1:].copy()
            fc_p50, fc_p10, fc_p90 = [], [], []
            for h in range(horizon):
                for quantile, label, lst in [
                    (0.5, "p50", fc_p50), (0.1, "p10", fc_p10), (0.9, "p90", fc_p90)
                ]:
                    pred = max(0, float(forecasts.get(label, [0])[-1]))
                    lst.append(pred)

            return np.array(fc_p50), np.array(fc_p10), np.array(fc_p90)

        except ImportError:
            # Fallback: quantile estimation from rolling statistics
            roll_mean = pd.Series(series).rolling(13).mean().iloc[-1]
            roll_std = pd.Series(series).rolling(13).std().iloc[-1]
            widening = np.sqrt(np.arange(1, horizon + 1))

            forecast = np.full(horizon, roll_mean)
            lower = np.maximum(0, forecast - 1.28 * roll_std * widening)
            upper = forecast + 1.28 * roll_std * widening

            return forecast, lower, upper


# ── Orchestrator ───────────────────────────────────────────────
def run_forecasts(
    demand_df: pd.DataFrame,
    sku: str,
    warehouse: str,
    horizon: int = 12,
    train_ratio: float = 0.85,
) -> List[ForecastResult]:
    """Run all three models on a single SKU-warehouse combination."""

    subset = demand_df[
        (demand_df["sku"] == sku) & (demand_df["warehouse"] == warehouse)
    ].sort_values("date")

    if len(subset) < 52:
        raise ValueError(f"Need ≥52 weeks of data, got {len(subset)}")

    series = subset["demand_units"].values.astype(float)
    dates = subset["date"].tolist()
    n = len(series)
    split = int(n * train_ratio)
    train = series[:split]
    test = series[split:]
    test_horizon = len(test)

    models = {
        "Holt-Winters": HoltWintersForecaster(),
        "Bayesian STS": BayesianForecaster(),
        "Quantile Regression": QuantileForecaster(),
    }

    results = []
    for name, model in models.items():
        fc, lo, hi = model.fit_predict(train, horizon=test_horizon)

        # Trim to match test length
        fc = fc[:test_horizon]
        lo = lo[:test_horizon]
        hi = hi[:test_horizon]

        result = ForecastResult(
            sku=sku,
            warehouse=warehouse,
            model_name=name,
            dates=dates[split:split+test_horizon],
            actuals=test,
            point_forecast=fc,
            lower_bound=lo,
            upper_bound=hi,
            mape=_mape(test, fc),
            rmse=_rmse(test, fc),
            coverage=_coverage(test, lo, hi),
        )
        results.append(result)

    return results


# ── Main entry point ───────────────────────────────────────────
if __name__ == "__main__":
    from pathlib import Path

    data_dir = Path(__file__).resolve().parent.parent / "data"
    demand = pd.read_csv(data_dir / "demand_history.csv", parse_dates=["date"])

    # Demo: forecast a high-volume SKU at Cork warehouse
    sku = "WM-PRO-BLK"
    warehouse = "Cork-IE"

    results = run_forecasts(demand, sku, warehouse)

    print(f"\n{'═'*60}")
    print(f"  Forecast Comparison: {sku} @ {warehouse}")
    print(f"{'═'*60}")
    for r in results:
        print(f"\n  {r.model_name}")
        print(f"    MAPE:     {r.mape:.1f}%")
        print(f"    RMSE:     {r.rmse:.1f}")
        print(f"    Coverage: {r.coverage:.1f}% (target: 80%)")

    # Save forecasts
    all_fc = pd.concat([r.to_dataframe() for r in results], ignore_index=True)
    all_fc.to_csv(data_dir / "forecast_results.csv", index=False)
    print(f"\n✓ Forecast results saved to data/forecast_results.csv")
