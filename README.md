# PayParity

A fair compensation benchmarking tool. Enter a role, location, years of
experience, and current salary, and PayParity predicts a fair salary from
those legitimate factors, shows the gap between actual and predicted pay,
and flags gaps larger than 5% for review.

CMSC 495 Capstone, University of Maryland Global Campus.

## Team

| Name | Role | Main contributions |
|---|---|---|
| Walid Atmar | Integration Lead + Architect | AI integration strategy, Design Rationale, architecture docs, CI/CD pipeline |
| Mimi Roa | Interface Designer + Architect | Interface Contracts, FastAPI endpoints, JWT auth, predictor wrapper, frontend client, test suite |

Erica Woods was originally Lead Architect and left the team partway through the course. Walid and Mimi shared the architect role after that.

## Features

- **Disparity Detection Engine.** A scikit-learn linear regression predicts
  expected salary from job title, location, years of experience, and
  department, and flags gaps above the threshold.
- **REST API.** Four versioned endpoints under `/api/v1` (see API below).
- **Transient gender field.** `gender` is accepted on a request but never
  stored or logged. A test (`test_gender_is_not_persisted`) enforces this.
- **Admin-only bulk import**, protected by JWT bearer tokens.
- **React + TypeScript frontend** with a single benchmark form.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Vitest |
| Backend | Python 3.11, FastAPI, Pydantic |
| AI / ML | scikit-learn `LinearRegression`, NumPy |
| Auth | PyJWT (HS256) |
| CI | GitHub Actions |

## Repository layout

```
backend/
  app/
    main.py            FastAPI app, CORS, /health
    routers/benchmark.py  API endpoints
    model/predictor.py    SalaryPredictor interface + regression model
    model/encoding.py     fixed-vocabulary categorical encoding
    auth.py            JWT verification
    schemas.py         request/response models
    store.py           in-memory result store
  tests/               pytest suite
  scripts/benchmark.py performance + model reliability benchmark
frontend/
  src/components/BenchmarkForm.tsx
  src/services/payParityClient.ts
.github/workflows/ci.yml
```

## Installation

**Requirements:** Python 3.11+, Node 20+, npm.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r ../requirements-dev.txt pytest-cov
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive API docs are at
`http://localhost:8000/docs`.

Optional environment variable:

| Variable | Default | Purpose |
|---|---|---|
| `PAYPARITY_JWT_SECRET` | `alpha-placeholder-secret` | Signing secret for admin tokens. Set a real value outside local dev. |

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). To point at a
different backend, set `VITE_API_BASE_URL` (default `http://localhost:8000`).

## User guide

1. Start the backend and the frontend.
2. Fill in **Job title**, **Location**, **Years of experience**, and
   **Current salary**. Known values are:
   - Roles: Software Engineer II, Senior Software Engineer, Staff Software Engineer
   - Locations: Austin, TX; Seattle, WA; New York, NY; San Francisco, CA; Remote
3. Click **Check fairness benchmark**.
4. Read the result:
   - **Predicted fair salary:** what the model expects for this profile.
   - **Confidence interval:** a range around the prediction.
   - **Gap:** how far current pay is from the prediction, in percent.
     Negative means paid below the prediction.
   - **Flagged for review:** shown when the gap is larger than 5% either way.

Unrecognized roles or locations still work, but they map to an "unknown"
bucket, so predictions for them are less reliable.

## API

Base path: `/api/v1`. Full schemas are at `/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/benchmark` | none | Run a fairness benchmark |
| GET | `/benchmark/{id}` | none | Fetch a saved result |
| GET | `/roles?query=` | none | Search known job titles |
| POST | `/salary-data` | admin JWT | Bulk import salary records |
| GET | `/health` | none | Health check (no `/api/v1` prefix) |

Example request:

```bash
curl -X POST http://localhost:8000/api/v1/benchmark \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Senior Software Engineer","location":"Seattle, WA",
       "years_experience":6,"department":"Engineering","current_salary":130000}'
```

Example response:

```json
{
  "benchmark_id": "b_08db287e",
  "predicted_fair_salary": 145575.68,
  "confidence_interval": [137575.68, 153575.68],
  "gap_percent": -10.7,
  "flagged": true,
  "generated_at": "2026-09-28T03:31:48Z"
}
```

Error responses:

| Status | Body | When |
|---|---|---|
| 401 | `{"error": "unauthorized"}` | Missing or invalid token |
| 403 | `{"error": "forbidden"}` | Token without `admin` role |
| 404 | `{"error": "not_found"}` | Unknown benchmark id |
| 422 | validation details | Missing field, blank text, negative experience, salary ≤ 0 |
| 503 | `{"error": "model_unavailable", "retryable": true}` | Model failure |

## Testing and quality

```bash
# backend
cd backend
python -m pytest --cov=app --cov-report=term    # tests + coverage
flake8 . && black --check .           # lint + format
python scripts/benchmark.py           # latency + model reliability

# frontend
cd frontend
npm run lint && npm run typecheck && npm run test && npm run build
```

Latest results:

| Check | Result |
|---|---|
| Backend tests | 16 passed |
| Backend coverage | 	97% (167 / 173 statements) |
| Frontend tests | 3 passed |
| flake8, black, ESLint, tsc | clean |
| Production bundle | 145 KB (47 KB gzipped) |
| API latency, 1,000 in-process requests | 	median ~2.2 ms, p99 ~2.7 ms |
| Model, training R² | 0.984 |
| Model, leave-one-out MAE | $7,235 |

Latency is measured in-process and excludes network and database time.

## CI/CD

GitHub Actions runs on every push and pull request to `main`:

- **Frontend:** install, lint, type check, test, build
- **Backend:** install, flake8, black, pytest with coverage (uploaded as
  the `backend-coverage` artifact), benchmark script

See [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md) for the branch and
review workflow.

## Known limitations

- Results are stored in memory and lost on restart. PostgreSQL is planned.
- The model is trained on 10 synthetic reference rows, not real pay data.
- The 5% flag threshold and the ±$8,000 confidence interval are fixed
  placeholders, not derived from model error.
- No login/token issuance endpoint yet; the JWT secret has a dev default.
- CORS allows all origins for local development.
- No deployment stage yet; the pipeline covers CI only.

See [ARCHITECTURE.md](ARCHITECTURE.md) for design details.
