"""Pydantic models matching Section 2 of the Interface Contracts document."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class BenchmarkRequest(BaseModel):
    job_title: str
    location: str
    years_experience: float = Field(ge=0)
    current_salary: float = Field(gt=0)
    # Transient-only: never written to the database or the in-memory
    # benchmark record. Used only for the duration of this request.
    gender: Optional[str] = None
    department: Optional[str] = None

    @field_validator("job_title", "location")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be blank")
        return v


class BenchmarkResult(BaseModel):
    benchmark_id: str
    predicted_fair_salary: float
    confidence_interval: List[float]
    gap_percent: float
    flagged: bool
    generated_at: str


class RolesResponse(BaseModel):
    roles: List[str]


class SalaryRecord(BaseModel):
    job_title: str
    location: str
    years_experience: float = Field(ge=0)
    salary: float = Field(gt=0)


class SalaryDataRequest(BaseModel):
    records: List[SalaryRecord]


class SalaryDataResponse(BaseModel):
    accepted: int
    rejected: int
    rejected_rows: List[int]


class ErrorResponse(BaseModel):
    error: str
    fields: Optional[List[str]] = None
    retryable: Optional[bool] = None
