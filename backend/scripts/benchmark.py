"""Performance and model-reliability benchmark for PayParity.

Run from backend/:  python scripts/benchmark.py

Latency is measured in-process with FastAPI's TestClient, so it covers
request validation, encoding, model prediction, and the store -- but
not network or database time.
"""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402
from app.model.encoding import (  # noqa: E402
    encode_department,
    encode_job_title,
    encode_location,
)
from app.model.predictor import (  # noqa: E402
    REFERENCE_COMPENSATION_DATA,
    RegressionSalaryPredictor,
)
from app.routers.benchmark import FLAG_THRESHOLD_PERCENT  # noqa: E402

REQUESTS = 1000
WARMUP = 50
SAMPLE_REQUEST = {
    "job_title": "Senior Software Engineer",
    "location": "Seattle, WA",
    "years_experience": 6,
    "department": "Engineering",
    "current_salary": 130000,
}


def percentile(sorted_values: list[float], pct: float) -> float:
    index = min(len(sorted_values) - 1, int(round(pct / 100 * len(sorted_values))) - 1)
    return sorted_values[max(index, 0)]


def benchmark_latency() -> None:
    client = TestClient(app)
    for _ in range(WARMUP):
        client.post("/api/v1/benchmark", json=SAMPLE_REQUEST)

    timings = []
    for _ in range(REQUESTS):
        start = time.perf_counter()
        response = client.post("/api/v1/benchmark", json=SAMPLE_REQUEST)
        timings.append((time.perf_counter() - start) * 1000)
        assert response.status_code == 200, response.text

    timings.sort()
    print(f"API latency over {REQUESTS} requests (ms)")
    print(f"  median {statistics.median(timings):.2f}")
    print(f"  p95    {percentile(timings, 95):.2f}")
    print(f"  p99    {percentile(timings, 99):.2f}")
    print(f"  max    {timings[-1]:.2f}")


def benchmark_model() -> None:
    start = time.perf_counter()
    predictor = RegressionSalaryPredictor()
    fit_ms = (time.perf_counter() - start) * 1000

    X = np.array(
        [
            (encode_job_title(t), encode_location(loc), yrs, encode_department(d))
            for t, loc, yrs, d, _ in REFERENCE_COMPENSATION_DATA
        ],
        dtype=float,
    )
    y = np.array([s for *_, s in REFERENCE_COMPENSATION_DATA], dtype=float)

    train_r2 = predictor._model.score(X, y)
    loo_pred = cross_val_predict(LinearRegression(), X, y, cv=LeaveOneOut())
    loo_mae = float(np.mean(np.abs(y - loo_pred)))
    gaps = np.abs(y - loo_pred) / loo_pred * 100
    within = int(np.sum(gaps <= FLAG_THRESHOLD_PERCENT))

    print("\nModel reliability")
    print(f"  training rows          {len(y)}")
    print(f"  fit time               {fit_ms:.1f} ms")
    print(f"  training R^2           {train_r2:.3f}")
    print(f"  leave-one-out MAE      ${loo_mae:,.0f}")
    print(
        f"  within {FLAG_THRESHOLD_PERCENT:.0f}% threshold    "
        f"{within}/{len(y)} (rest would be flagged)"
    )


if __name__ == "__main__":
    benchmark_latency()
    benchmark_model()
