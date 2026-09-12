""" Categorical encoding for the model layer.

Fixed, versioned vocabularies for job title, location, and department.
Unrecognized values map to a dedicated "unknown" bucket rather than
growing the table at runtime, so train-time and serve-time encodings
can never drift apart, and memory use is bounded regardless of how many
distinct free-text values the API receives.

Follow-up (still open, tracked as tech debt): this vocabulary is
hand-maintained here rather than persisted/versioned alongside a trained
model artifact. Fine for an Alpha slice; before Beta, move it to a file
saved next to the trained model so the two can never fall out of sync.
"""

from __future__ import annotations

ENCODING_VOCAB_VERSION = "v2-fixed-vocab"

KNOWN_ROLES = [
    "Software Engineer II",
    "Senior Software Engineer",
    "Staff Software Engineer",
]

KNOWN_LOCATIONS = [
    "Austin, TX",
    "Seattle, WA",
    "New York, NY",
    "San Francisco, CA",
    "Remote",
]

KNOWN_DEPARTMENTS = [
    "Engineering",
    "Product",
    "Data",
    "Design",
    "unspecified",
]


def _build_index(values: list[str]) -> dict[str, int]:
    return {v.strip().lower(): i for i, v in enumerate(values)}


_JOB_TITLE_INDEX = _build_index(KNOWN_ROLES)
_LOCATION_INDEX = _build_index(KNOWN_LOCATIONS)
_DEPARTMENT_INDEX = _build_index(KNOWN_DEPARTMENTS)

# Reserved codes for values outside the known vocabulary, one past the
# last real index in each table -- stable regardless of table size.
UNKNOWN_JOB_TITLE = len(KNOWN_ROLES)
UNKNOWN_LOCATION = len(KNOWN_LOCATIONS)
UNKNOWN_DEPARTMENT = len(KNOWN_DEPARTMENTS)


def _encode(value: str, index: dict[str, int], unknown_code: int) -> int:
    """Looks up a value in a fixed vocabulary; never mutates the table."""
    key = (value or "").strip().lower()
    return index.get(key, unknown_code)


def encode_job_title(value: str) -> int:
    return _encode(value, _JOB_TITLE_INDEX, UNKNOWN_JOB_TITLE)


def encode_location(value: str) -> int:
    return _encode(value, _LOCATION_INDEX, UNKNOWN_LOCATION)


def encode_department(value: str | None) -> int:
    return _encode(value or "unspecified", _DEPARTMENT_INDEX, UNKNOWN_DEPARTMENT)


def search_roles(query: str) -> list[str]:
    q = query.strip().lower()
    if not q:
        return list(KNOWN_ROLES)
    return [r for r in KNOWN_ROLES if q in r.lower()]
