# AGENTS

Purpose: concise instructions to help AI coding agents work productively in this repository.

Key references
- Primary spec: [task.md](task.md#L1-L200)

What agents should know
- This repository contains an assignment: implement a SHACL-driven food-ordering backend (Python) that serves JSON-LD documents and SHACL shapes. A minimal frontend will be added later (deferred).
- Required endpoints: retrieve form schema for a dish; submit & validate a filled-in form. Validation must run on the backend and return structured errors (JSON with field name, error type, message).
- Add new dishes by adding JSON-LD + SHACL shape files only — no frontend changes should be necessary.

Conventions & expectations
- Keep changes minimal and focused. Preserve separation of concerns: backend handles translation from SHACL/JSON-LD to frontend form schema.
- Include a clear README with reproducible setup and run instructions when you add runnable code.
- Add tests that demonstrate both valid and invalid submissions (SHACL validation cases).

Agent workflow (quick checklist)
1. Read the primary spec: [task.md](task.md#L1-L200).
2. Implement backend in **Python** (use RDFLib, pySHACL, or similar for RDF/SHACL).
3. When implementing: include `README.md`, automated tests (see `tests/` for payload examples), and a lightweight run script.
4. Add implementation files under `backend/` or `server/` folder. Store JSON-LD and SHACL shapes in `backend/data/` or similar.
5. Tests: include `tests/` folder with valid/invalid payload examples and their expected SHACL validation results.

Files to check first
- [task.md](task.md#L1-L200)

Links
- SHACL primer: https://www.w3.org/TR/shacl/
- JSON-LD primer: https://www.w3.org/TR/json-ld/

If this repo grows in complexity, consider adding domain-specific agent instructions under `.github/` or expanding this file with per-component notes.
