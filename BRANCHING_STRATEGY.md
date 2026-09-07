# PayParity Branching Strategy

## Team
- Mimi Roa — Interface Designer
- Walid Atmar — Integration Lead

(Erica Woods, originally Lead Architect, dropped the course; the team is now two people.)

## Model: GitHub Flow (lightweight, adapted from GitFlow)

Full GitFlow (separate `develop`, `release`, and `hotfix` branches) is designed for larger teams with staged release cycles. For a two-person team on a single deliverable, we use a leaner adaptation:

- `main` is always deployable. No direct commits to `main`.
- Short-lived feature branches are created off `main` for each scoped unit of work, e.g.:
  - `feature/interface-contracts`
  - `feature/auth-jwt`
  - `feature/model-wrapper`
  - `feature/frontend-dashboard`
- Each feature branch is opened as a pull request against `main` when ready for review.
- At least one reviewer (the other teammate) must approve before merge.
- CI (GitHub Actions) must pass (lint, type check, tests, build) before a PR is eligible to merge.
- Branch protection on `main` enforces both the required review and passing CI status checks.

## Why this fits a 2-person team

With only two contributors, a multi-branch GitFlow model (develop/release/hotfix) adds process overhead without a corresponding benefit, since there is no large batch of parallel features requiring staged integration. Short-lived feature branches with mandatory PR review give both people visibility into every change while keeping the workflow simple enough to sustain given course timelines.

## AI-assisted code policy

- AI-assisted code (e.g., drafted with Claude) is permitted for boilerplate, documentation, and scaffolding (TypeScript interfaces, Python Protocol definitions, test scaffolding).
- Any PR containing AI-generated code must disclose this in the PR template.
- AI-generated code must be reviewed line by line by a human teammate before merge; passing CI tests alone is not sufficient sign-off.
- Special attention is given to business logic (disparity threshold calculations) and sensitive data handling (e.g., the `gender` field remaining transient-only and never persisted).
