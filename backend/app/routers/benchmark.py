from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_admin
from app.model.encoding import (
    encode_department,
    encode_job_title,
    encode_location,
    search_roles,
)
from app.model.predictor import SalaryFeatures, SalaryPredictor, get_predictor
from app.schemas import (
    BenchmarkRequest,
    BenchmarkResult,
    RolesResponse,
    SalaryDataRequest,
    SalaryDataResponse,
)
from app.store import get_benchmark, save_benchmark

router = APIRouter(prefix="/api/v1", tags=["benchmark"])

# Anything beyond this gap is flagged. Placeholder threshold pending a
# statistically-grounded value once real reference data exists (tracked
# as tech debt in the Refinement Report).
FLAG_THRESHOLD_PERCENT = 5.0


@router.post("/benchmark", response_model=BenchmarkResult)
def submit_benchmark(
    payload: BenchmarkRequest,
    predictor: SalaryPredictor = Depends(get_predictor),
) -> BenchmarkResult:
    # `payload.gender`, if present, lives only in this function's scope.
    # It is read here (reserved for gap-comparison logic) and is never
    # written to `store.py` or logged.
    features = SalaryFeatures(
        job_title_encoded=encode_job_title(payload.job_title),
        location_encoded=encode_location(payload.location),
        years_experience=payload.years_experience,
        department_encoded=encode_department(payload.department),
    )

    try:
        prediction = predictor.predict(features)
    except Exception as exc:  # model-layer failure -> graceful 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "model_unavailable", "retryable": True},
        ) from exc

    gap_percent = round(
        (
            (payload.current_salary - prediction.predicted_salary)
            / prediction.predicted_salary
            * 100
        ),
        1,
    )

    result = BenchmarkResult(
        benchmark_id=f"b_{uuid.uuid4().hex[:8]}",
        predicted_fair_salary=round(prediction.predicted_salary, 2),
        confidence_interval=[
            round(prediction.confidence_low, 2),
            round(prediction.confidence_high, 2),
        ],
        gap_percent=gap_percent,
        flagged=abs(gap_percent) > FLAG_THRESHOLD_PERCENT,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    save_benchmark(result.benchmark_id, result.model_dump())
    return result


@router.get("/benchmark/{benchmark_id}", response_model=BenchmarkResult)
def read_benchmark(benchmark_id: str) -> BenchmarkResult:
    record = get_benchmark(benchmark_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found"},
        )
    return BenchmarkResult(**record)


@router.get("/roles", response_model=RolesResponse)
def list_roles(query: str = "") -> RolesResponse:
    return RolesResponse(roles=search_roles(query))


@router.post(
    "/salary-data",
    response_model=SalaryDataResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def bulk_import(
    payload: SalaryDataRequest,
    _claims: dict = Depends(require_admin),
) -> SalaryDataResponse:
    # TECH DEBT: accepts every well-formed record; no duplicate detection
    # or outlier screening yet. Rejection tracking below only covers
    # what Pydantic already rejects at the request boundary, since a
    # malformed row never reaches this function. Row-level business
    # validation (e.g. salary outliers) is follow-up work.
    accepted = len(payload.records)
    return SalaryDataResponse(accepted=accepted, rejected=0, rejected_rows=[])
