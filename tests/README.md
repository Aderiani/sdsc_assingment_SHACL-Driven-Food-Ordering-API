# Test Payloads

This folder contains examples of valid and invalid submissions for SHACL validation testing.

## Structure
- `valid/`: Valid payload examples that should pass SHACL validation.
- `invalid/`: Invalid payload examples with their expected SHACL validation errors.
- `README.md`: Description of each test case and its expected outcome.

## Adding Tests
For each dish and validation scenario:
1. Create a JSON file with the test payload.
2. Document the expected SHACL validation result (errors or success).
3. Reference the dish's SHACL shape in `backend/data/shapes/` (or similar).

## Notes on Payload Shape
Payload bodies should contain only dish-specific fields.
The dish is selected by route using `dish_id`, for example:

- `POST /dishes/french-tacos/order`
- `POST /dishes/ramen/order`

This means the payload does not need a `dish` field.

## Example Test Case
- **File**: `valid/french-tacos-01.json`
- **Expected**: ✅ Valid (passes SHACL validation)

```json
{
  "size": "large",
  "filling": "chicken",
  "sauce": "harissa"
}
```

- **File**: `invalid/french-tacos-missing-size.json`
- **Expected**: ❌ Invalid (SHACL validation error)
  - Error: Field `size` is required but missing.

```json
{
  "filling": "chicken",
  "sauce": "harissa"
}
```
