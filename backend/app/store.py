"""In-memory persistence for Alpha.

TECH DEBT: Section 2.2 (GET /api/v1/benchmark/{id}) implies durable
storage, but the interface contracts leave the database schema to the
Lead Architect's diagram, which no longer has an owner. Rather than
guess at a schema, this Alpha stores benchmark results in-process so the
API contract and multi-module flow can be demonstrated end-to-end now.
Swapping this for real PostgreSQL persistence is the single highest
priority piece of follow-up work before Beta, and should be a fairly
small change since callers only interact with this module's functions.
"""

from __future__ import annotations

from typing import Optional

_benchmarks: dict[str, dict] = {}


def save_benchmark(benchmark_id: str, result: dict) -> None:
    _benchmarks[benchmark_id] = result


def get_benchmark(benchmark_id: str) -> Optional[dict]:
    return _benchmarks.get(benchmark_id)
