# PayParity — System Architecture (Alpha Release)

**Owner:** Lead Architect
**Status:** Alpha — core modules integrated and running end to end on sample data

## 1. Overview

PayParity is a fair compensation benchmarking tool. For the Alpha release, the goal isn't a polished product — it's proof that the full pipeline works: a user can submit compensation data, the system runs it through the Disparity Detection Engine, and the result comes back and renders in the UI. Every module below is wired together and passing through CI; individual pieces still have rough edges called out in "Known limitations."

## 2. System Diagram

```mermaid
flowchart LR
    subgraph Client
        A[React + TypeScript SPA]
    end

    subgraph API["Backend — FastAPI"]
        B[Auth / Request Layer]
        C[Compensation Data Service]
        D[Disparity Detection Engine\n(scikit-learn regression)]
    end

    subgraph Data
        E[(PostgreSQL)]
    end

    subgraph Infra["AWS"]
        F[App server / container]
        G[CI/CD Pipeline\nGitHub Actions]
    end

    A -- REST/JSON --> B
    B --> C
    C --> E
    C --> D
    D --> C
    C -- results --> B
    B -- JSON response --> A
    G -- deploys --> F
    F -.hosts.-> API
```

## 3. Component Breakdown

**Frontend (React + TypeScript)**
Single-page app with a basic dashboard: a form to submit or select a dataset, and a results table showing flagged pay disparities. No advanced filtering, sorting, or visualization yet — that's polish for Beta.

**Backend (Python/FastAPI)**
Exposes the API the frontend calls. For Alpha this covers:
- `POST /api/compensation` — ingest/store compensation records
- `POST /api/disparity-analysis` — run the detection engine against a dataset and return flagged results
- Basic request validation and error handling on both endpoints

**Database (PostgreSQL)**
Stores compensation records (role, experience, location, tenure, pay) and analysis results. Schema is functional but minimal — no migrations tooling yet, just a baseline schema applied manually.

**Disparity Detection Engine (scikit-learn)**
A regression model that predicts expected compensation from legitimate factors (role, experience, location, tenure) and flags individuals whose actual pay deviates significantly from the prediction. In Alpha it runs on a static/sample dataset, not live production data, and uses a fixed significance threshold rather than a tunable one.

**Deployment (AWS)**
The app runs on a single environment (no separate staging/prod split yet). The CI/CD pipeline (established in Unit 4) runs tests and deploys on merge to main.

## 4. Multi-Module Integration — What "Alpha" Demonstrates

- Frontend → Backend → Database → ML engine → back to Frontend is a complete, working round trip on sample data.
- The Disparity Detection Engine is called synchronously from the API layer, not just runnable as a standalone script — this is the integration point that proves the AI feature is a real part of the product, not a demo off to the side.
- CI/CD runs on every push: linting, unit tests for the API and the regression module, and a build step.

## 5. Known Limitations (Alpha, not yet resolved)

- Single environment / no environment-specific config yet
- Detection threshold is hardcoded rather than configurable per analysis
- No database migration tooling — schema changes are applied manually
- Frontend results view is functional but not designed for large datasets

*(These are being tracked and will be addressed as part of the team's ongoing peer review and refinement process.)*

## 6. Version Control Practices

- Feature branches per module, merged to `main` via pull request
- CI must pass before merge
- Commit messages describe the change and its scope (e.g. `feat(api): add disparity-analysis endpoint`, `fix(engine): correct regression feature scaling`)
