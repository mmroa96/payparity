## Summary

What does this PR change, and why?

## Related interface contract(s)

Which endpoint(s), TypeScript interface(s), or model wrapper method(s) from `interface-contracts.md` does this touch?

## Testing

- [ ] New/updated unit tests added (pytest / Jest)
- [ ] Existing tests pass locally
- [ ] CI pipeline passes (lint, type check, tests, build)

## AI-assisted development disclosure

- [ ] This PR includes AI-generated or AI-assisted code
- If checked, describe what was AI-generated and what was hand-written/modified:

## AI code review checklist (required if any box above is checked)

- [ ] Reviewed line by line by a human teammate (not merged on the basis of passing tests alone)
- [ ] Business logic verified (e.g., disparity threshold / regression logic matches the spec, not just plausible-looking code)
- [ ] Sensitive fields checked (e.g., `gender` remains transient-only and is never persisted to the database or logs)
- [ ] No hardcoded secrets, credentials, or environment-specific values introduced

## Reviewer sign-off

- [ ] Reviewed by: ____________________
- [ ] Approved to merge into `main`
