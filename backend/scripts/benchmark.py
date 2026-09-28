"""Performance and model-reliability benchmark for PayParity.

Run from backend/:  python scripts/benchmark.py

Latency is measured in-process with FastAPI's TestClient, so it covers
request validation, encoding, model prediction, and the store -- but
not network or database time.

The reliability check refits the same model type on the same reference
rows used in app/model/predictor.py and scores it with leave-one-out
cross-validation. REFERENCE_X / REFERENCE_Y below mirror those rows and
must be kept in sync if the training data changes.
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
from app.model.predictor import RegressionSalaryPredictor  # noqa: E402
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

# Mirrors the reference data in RegressionSalaryPredictor.
# Columns: job_title_encoded, location_encoded, years_experience,
# department_encoded
REFERENCE_X = np.array(
    [
        [0, 0, 1, 0],
        [0, 0, 3, 0],
        [0, 0, 6, 0],
        [1, 0, 6, 0],
        [1, 1, 8, 0],
        [2, 0, 10, 0],
        [0, 1, 2, 1],
        [1, 1, 5, 1],
        [2, 1, 9, 1],
        [1, 2, 4, 0],
    ],
    dtype=float,
)
REFERENCE_Y = np.array(
    [
        85000,
        105000,
        135000,
        152000,
        168000,
        190000,
        90000,
        140000,
        175000,
        125000,
    ],
    dtype=float,
)


def percentile(sorted_values: list[float], pct: float) -> float:
    index = int(round(pct / 100 * len(sorted_values))) - 1
    return sorted_values[max(0, min(index, len(sorted_values) - 1))]


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
    RegressionSalaryPredictor()
    fit_ms = (time.perf_counter() - start) * 1000

    X, y = REFERENCE_X, REFERENCE_Y
    train_r2 = LinearRegression().fit(X, y).score(X, y)
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
