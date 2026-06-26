# SHACL-Driven Food Ordering API

Minimal, data-driven backend for rendering and validating food-ordering forms using JSON-LD + SHACL.

This repository exposes dish definitions (JSON-LD) and SHACL shapes and provides:

- a Python FastAPI backend that generates frontend form schema from SHACL and validates submissions
- a tiny static frontend that renders the generated schema and submits orders

## Goals

- Keep the frontend generic: render any dish schema returned by the backend.
- Keep the backend data-driven: add a new dish by adding JSON-LD + SHACL files under `backend/data/`.

## Design Assumptions

1. `dish_id` is the API contract for selecting the dish schema.

   - The backend will use `GET /dishes/{dish_id}/schema` and `POST /dishes/{dish_id}/order`.
   - The payload body contains only dish-specific form fields; the dish is determined from the route.
2. Error responses use a structured validation format with an `errors` array:

   - `valid`, `errors`
   - `errors[]` contains `field`, `constraint`, and `message`
3. The backend translates SHACL shapes to a JSON Schema-like form schema.

   - This keeps the frontend generic and avoids hardcoding dish-specific logic.
4. Field constraints in the current test documents are assumptions for the implementation.

   - Examples: French Tacos `size` values are assumed to be `small`, `medium`, `large`.
   - Ramen `spiciness` is assumed to be an integer range `0-5`.
5. Backend JSON-LD and SHACL files are versioned in git.

   - The planned storage location is `backend/data/`.
   - Adding a new dish should require only a new JSON-LD document and matching SHACL shape.
6. Hot reload of shapes is a potential future enhancement.

   - The initial implementation will load shapes at startup for simplicity and consistent validation.
7. Reproducibility is based on a Python virtual environment and `requirements.txt`.

   - The repository will use a one-command startup design and CI-run tests on every pull request.
   - The backend will also be usable via `curl` for manual integration verification.

## Quick links

- Data: `backend/data/`
- Frontend: `frontend/` (static files)
- Dev launcher: `start.sh` (launches backend + frontend)
- Tests: `tests/`

## Requirements

- Python 3.11+ (3.14 recommended for dev environments when available)
- A POSIX-compatible shell for `start.sh` (Linux/macOS)
- Dependencies: see `requirements.txt`

## Quickstart

1. Make executable and run the integrated dev launcher:

```bash
chmod +x start.sh
./start.sh
```

`start.sh` will:

- create and/or use a `.venv` virtual environment
- install dependencies from `requirements.txt` if missing
- start the backend (uvicorn) on `127.0.0.1:8000`
- start the static frontend on `127.0.0.1:8001`
- open your browser to `http://127.0.0.1:8001`
- trap `INT/TERM` and perform a targeted, graceful shutdown of child processes

## Detailed Usage Manual

If you prefer to run components manually:

```bash
# backend only
python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# frontend only (serve from repo root)
python3 -m http.server --bind 127.0.0.1 8001 -d frontend
```

### API (backend)

The backend exposes the following endpoints:

- `GET /dishes` — list available dishes (id and label)
- `GET /dishes/{dish_id}/schema` — return form schema generated from SHACL for `dish_id`
- `POST /dishes/{dish_id}/order` — validate a submission against the dish's SHACL shape

### Error/validation format

The backend returns a structured validation payload:

```json
{
   "valid": false,
   "errors": [
      { "field": "size", "constraint": "sh:minCount", "message": "Field 'size' is required." }
   ]
}
```

The frontend additionally maps SHACL report details into human-friendly messages before showing them to users.

### Data layout

Each dish lives in `backend/data/<dish-id>/` and contains at least:

- `dish.jsonld` — human-readable JSON-LD metadata
- `shape.ttl` — SHACL shape

For detailed guide of how to generate such files see docs.

### Add a new dish

To add a new dish, create a folder under `backend/data/` with `dish.jsonld` and `shape.ttl`. The backend will discover it on startup.

### API Contract

Recommended endpoints:

- `GET /dishes` — list available dish identifiers and labels.
- `GET /dishes/{dish_id}/schema` — return the generated form schema for the requested dish.
- `POST /dishes/{dish_id}/order` — submit a filled form for validation.

Example error response format:

```json
{
  "valid": false,
  "errors": [
    {
      "field": "size",
      "constraint": "sh:minCount",
      "message": "Field 'size' is required."
    },
    {
      "field": "spiciness",
      "constraint": "sh:maxExclusive",
      "message": "Value 10 exceeds the allowed range."
    }
  ]
}
```

### Example curl Usage

```bash
curl -X GET http://localhost:8000/dishes/french-tacos/schema

curl -X POST http://localhost:8000/dishes/french-tacos/order \
  -H "Content-Type: application/json" \
  -d '{"size":"large","filling":"chicken","sauce":"harissa","notes":"No onions please"}'
```

## Tests

Run the test suite inside the virtual environment:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest
```

## Test Coverage

The `tests/` folder contains both valid and invalid payloads for French Tacos and Ramen.
The invalid set now covers:

- missing required fields
- invalid enumeration values
- out-of-range numeric values
- empty-string edge cases
- `null` values
- array cardinality violations

## Continuous Integration

A GitHub Actions workflow is configured in `.github/workflows/python-tests.yml` to run the backend test suite on every push and pull request to `main`.
The workflow installs required system packages, installs Python dependencies, and executes `python3 -m pytest -q`.

## Notes

- CORS: For development the backend enables CORS to allow the standalone frontend on `127.0.0.1:8001`. For production, restrict origins in `backend/app.py`.
- The frontend's API base URL is `http://127.0.0.1:8000` by default (see `frontend/index.html` if you need to change it).

## Improvement Ideas

- idea1
- diea2
- idea3
