"""Categorical encoding for the model layer.

TECH DEBT: these are fixed, hardcoded lookup tables rather than encoders
persisted/versioned alongside a trained model artifact. Fine for an Alpha
slice with a synthetic dataset; before Beta this should move to a proper
encoder saved next to the trained model so train-time and serve-time
encodings can never drift apart.
"""
from __future__ import annotations

KNOWN_ROLES = [
    "Software Engineer II",
    "Senior Software Engineer",
    "Staff Software Engineer",
]

_JOB_TITLE_INDEX = {name: i for i, name in enumerate(KNOWN_ROLES)}
_LOCATION_INDEX: dict[str, int] = {}
_DEPARTMENT_INDEX: dict[str, int] = {}


def _encode(value: str, index: dict[str, int]) -> int:
    """Assigns a stable integer to each distinct value seen so far.

    TECH DEBT: this grows unbounded in memory and resets on restart. A
    real implementation would encode against a fixed, versioned vocabulary.
    """
    key = value.strip().lower()
    if key not in index:
        index[key] = len(index)
    return index[key]


def encode_job_title(value: str) -> int:
    return _encode(value, _JOB_TITLE_INDEX)


def encode_location(value: str) -> int:
    return _encode(value, _LOCATION_INDEX)


def encode_department(value: str | None) -> int:
    return _encode(value or "unspecified", _DEPARTMENT_INDEX)


def search_roles(query: str) -> list[str]:
    q = query.strip().lower()
    if not q:
        return list(KNOWN_ROLES)
    return [r for r in KNOWN_ROLES if q in r.lower()]
