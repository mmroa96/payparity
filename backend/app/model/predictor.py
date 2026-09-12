"""Backend -> ML model interface, per Interface Contracts section 3.2.

The model is hosted in-process within the backend service (confirmed with
Integration Lead), so calling it is a direct function call, not a network
hop. This module wraps scikit-learn behind a stable Protocol so the model
can be retrained or swapped without changing the API contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass
class SalaryFeatures:
    job_title_encoded: int
    location_encoded: int
    years_experience: float
    department_encoded: int


@dataclass
class SalaryPrediction:
    predicted_salary: float
    confidence_low: float
    confidence_high: float


class SalaryPredictor(Protocol):
    def predict(self, features: SalaryFeatures) -> SalaryPrediction: ...


class RegressionSalaryPredictor:
    """Alpha implementation: a linear regression trained on a small
    synthetic reference dataset.

    TECH DEBT: the reference dataset below is synthetic/placeholder, not
    real compensation data. It exists to prove the interface end-to-end
    for the Alpha release. Swapping in a real, larger, and periodically
    retrained dataset (likely fed by POST /api/v1/salary-data) is tracked
    as follow-up work before Beta.
    """

    def __init__(self) -> None:
        self._model = LinearRegression()
        self._interval_width = 8000.0  # placeholder fixed-width CI, see README
        self._fit_on_synthetic_data()

    def _fit_on_synthetic_data(self) -> None:
        # Columns: job_title_encoded, location_encoded, years_experience, department_encoded
        X = np.array(
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
            ]
        )
        y = np.array(
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
            ]
        )
        self._model.fit(X, y)

    def predict(self, features: SalaryFeatures) -> SalaryPrediction:
        X = np.array(
            [
                [
                    features.job_title_encoded,
                    features.location_encoded,
                    features.years_experience,
                    features.department_encoded,
                ]
            ]
        )
        predicted = float(self._model.predict(X)[0])
        return SalaryPrediction(
            predicted_salary=predicted,
            confidence_low=predicted - self._interval_width,
            confidence_high=predicted + self._interval_width,
        )


_predictor_singleton: SalaryPredictor | None = None


def get_predictor() -> SalaryPredictor:
    """FastAPI dependency: reuse one fitted model per process."""
    global _predictor_singleton
    if _predictor_singleton is None:
        _predictor_singleton = RegressionSalaryPredictor()
    return _predictor_singleton
