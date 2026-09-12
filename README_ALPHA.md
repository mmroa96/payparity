# PayParity — Alpha slice (frontend + API contract)

This covers the frontend + API contract implementation half of the Unit 5 split.
Drop `backend/` and `frontend/src/` into the existing `payparity` monorepo
alongside Walid's model integration work.

## What's implemented and working

- `POST /api/v1/benchmark`, `GET /api/v1/benchmark/{id}`, `GET /api/v1/roles`,
  `POST /api/v1/salary-data` — all four endpoints from Interface Contracts
  section 2, matching the request/response shapes and error codes exactly.
- JWT auth boundary (section 3.3): bulk import requires a valid bearer token
  with an `admin` role claim; missing/invalid token -> 401, wrong role -> 403.
- `SalaryPredictor` Protocol + scikit-learn `LinearRegression` implementation
  (section 3.2), run in-process as a direct function call.
- `gender` is read only inside the request handler and never written to the
  in-memory store — covered by `test_gender_is_not_persisted`.
- Frontend `PayParityClient` (section 3.1) implementing the exact interface,
  translating camelCase <-> the API's snake_case at the boundary.
- 11 passing pytest tests covering the happy path, validation errors, the
  gender-transience guarantee, and the auth boundary.

## Known tech debt (flagged intentionally, for the Refinement Report)

1. **No real database.** Benchmarks live in an in-process dict (`store.py`),
   not PostgreSQL. Highest-priority item before Beta; the module boundary is
   already isolated so this should be a contained change.
2. **Synthetic training data.** The model is fit on 10 hardcoded rows to
   prove the interface, not real compensation data.
3. **Unbounded in-memory encoders.** `encoding.py`'s location/department
   encoders grow forever and reset on restart; needs a fixed, versioned
   vocabulary before Beta.
4. **Hardcoded JWT secret, no issuance flow.** There's no login endpoint yet;
   tests mint tokens directly. Needs real secret management on AWS.
5. **CORS wide open (`*`)** for local dev convenience.
6. **Fixed 5% flag threshold** with no statistical grounding yet.

## Running locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# in another terminal:
pytest tests/ -v
```

Frontend files assume `VITE_API_BASE_URL` is set (defaults to
`http://localhost:8000`) and are meant to be copied into the existing Vite/CRA
React app structure.
