"""Tests for the Integration Lead's part of the model layer:
encoding.py's fixed vocabulary and predictor.py's reference dataset.

Kept separate from test_benchmark.py (Mimi's file) so ownership of each
test file stays clear.
"""

from app.model.encoding import (
    UNKNOWN_DEPARTMENT,
    UNKNOWN_JOB_TITLE,
    UNKNOWN_LOCATION,
    encode_department,
    encode_job_title,
    encode_location,
)
from app.model.predictor import RegressionSalaryPredictor, SalaryFeatures


def test_known_values_get_stable_codes():
    first = encode_job_title("Senior Software Engineer")
    second = encode_job_title("senior software engineer")  # case-insensitive
    assert first == second
    assert first != UNKNOWN_JOB_TITLE


def test_unknown_values_map_to_unknown_bucket_not_a_growing_table():
    before = encode_location("A Location Nobody Has Used Before")
    after = encode_location("A Completely Different Unseen Location")
    assert before == UNKNOWN_LOCATION
    assert after == UNKNOWN_LOCATION  # same bucket, table never grew


def test_department_defaults_to_unspecified():
    assert encode_department(None) == encode_department("unspecified")
    assert encode_department("nonexistent-department") == UNKNOWN_DEPARTMENT


def test_predictor_produces_higher_salary_for_more_senior_role():
    predictor = RegressionSalaryPredictor()

    junior = predictor.predict(
        SalaryFeatures(
            job_title_encoded=encode_job_title("Software Engineer II"),
            location_encoded=encode_location("Seattle, WA"),
            years_experience=2,
            department_encoded=encode_department("Engineering"),
        )
    )
    staff = predictor.predict(
        SalaryFeatures(
            job_title_encoded=encode_job_title("Staff Software Engineer"),
            location_encoded=encode_location("Seattle, WA"),
            years_experience=10,
            department_encoded=encode_department("Engineering"),
        )
    )

    assert staff.predicted_salary > junior.predicted_salary


def test_predictor_returns_a_confidence_interval_around_the_point_estimate():
    predictor = RegressionSalaryPredictor()
    result = predictor.predict(
        SalaryFeatures(
            job_title_encoded=encode_job_title("Senior Software Engineer"),
            location_encoded=encode_location("Remote"),
            years_experience=6,
            department_encoded=encode_department("Engineering"),
        )
    )
    assert result.confidence_low < result.predicted_salary < result.confidence_high
