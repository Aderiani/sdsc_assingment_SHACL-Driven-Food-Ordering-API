<!-- Minimal Copilot instructions for code assistants -->

# Repository assistant guidance

This project is a SHACL-driven food-ordering API prototype. The authoritative project description is in [task.md](../task.md#L1-L200).

Assistant responsibilities
- Prefer small, focused PRs that implement features in a top-level `backend/` or `server/` folder.
- When adding code, include `README.md` with exact setup and run steps and add tests demonstrating SHACL validation behavior.
- Preserve the principle: backend translates SHACL/JSON-LD into a frontend-consumable form schema; frontend must remain generic.

Quick checks before code changes
- Ensure SHACL validation runs on the backend and returns structured errors.
- Ensure new dishes are added solely via JSON-LD + SHACL files.

Where to document decisions
- Use `docs/` for architecture notes and modelling choices (SHACL/JSON-LD rationale).
