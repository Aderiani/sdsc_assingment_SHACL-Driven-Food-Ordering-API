# SHACL-Driven Food Ordering API

This repository is a design and validation scaffold for a SHACL-driven food ordering backend.
The backend is intended to be implemented in Python using RDFLib + pySHACL.
The frontend is intentionally generic: it should render schema returned by the backend and submit payloads without dish-specific logic.

## Repository Contents

- `docs/MODELLING.md` — modelling decisions, assumptions, and translation rules for JSON-LD, SHACL, and frontend schema.
- `tests/` — valid and invalid payload examples plus runtime expectations.
- `.github/workflows/ci.yml` — CI workflow that installs dependencies and runs tests on pull requests.
- `requirements.txt` — Python dependencies for the backend and test tooling.

## Design Assumptions

1. `dish_id` is the API contract for selecting the dish schema.
   - The backend will use `GET /dishes/{dish_id}/schema` and `POST /dishes/{dish_id}/order`.
   - The payload body contains only dish-specific form fields; the dish is determined from the route.

2. Error responses use a structured format based on RFC 7807 Problem Details with a `violations` array:
   - `type`, `title`, `status`, `detail`
   - `violations[]` contains `field`, `code`, and `message`

3. The backend translates SHACL shapes to a JSON Schema-like form schema.
   - This keeps the frontend generic and avoids hardcoding dish-specific logic.

4. Field constraints in the current test documents are assumptions for the implementation.
   - Examples: French Tacos `size` values are assumed to be `small`, `medium`, `large`.
   - Ramen `spiciness` is assumed to be an integer range `0-5`.

5. CORS is not required for the initial API design.
   - If the frontend is later served from a different origin, CORS can be added via a thin middleware layer.

6. Backend JSON-LD and SHACL files are versioned in git.
   - The planned storage location is `backend/data/`.
   - Adding a new dish should require only a new JSON-LD document and matching SHACL shape.

7. Hot reload of shapes is a potential future enhancement.
   - The initial implementation will load shapes at startup for simplicity and consistent validation.

8. Reproducibility is based on a Python virtual environment and `requirements.txt`.
   - The repository will use a one-command startup design and CI-run tests on every pull request.
   - The backend will also be usable via `curl` for manual integration verification.

## API Contract

Recommended endpoints:

- `GET /dishes` — list available dish identifiers and labels.
- `GET /dishes/{dish_id}/schema` — return the generated form schema for the requested dish.
- `POST /dishes/{dish_id}/order` — submit a filled form for validation.

Example error response format:

```json
{
  "type": "https://example.com/probs/validation",
  "title": "Validation Failed",
  "status": 400,
  "detail": "One or more form fields failed validation.",
  "violations": [
    {
      "field": "/size",
      "code": "required",
      "message": "Field 'size' is required."
    },
    {
      "field": "/spiciness",
      "code": "range",
      "message": "Value 10 exceeds maximum allowed value of 5."
    }
  ]
}
```

## Example curl Usage

```bash
curl -X GET http://localhost:8000/dishes/french-tacos/schema

curl -X POST http://localhost:8000/dishes/french-tacos/order \
  -H "Content-Type: application/json" \
  -d '{"size":"large","filling":"chicken","sauce":"harissa","notes":"No onions please"}'
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

## Development Notes

This repository is currently structured for backend implementation.
The next development step is to add a Python backend under `backend/` that loads JSON-LD and SHACL shapes, generates form schema dynamically, and returns structured validation errors.
