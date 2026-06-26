# SHACL/JSON-LD Modelling Choices

This document captures the design decisions for mapping dish definitions into JSON-LD, validating them with SHACL, and translating the result into a frontend-friendly schema.

## Overview

Each dish is represented as a JSON-LD document that declares dish-specific properties and metadata.
A separate SHACL shape constrains the expected form fields for that dish.
The backend will load the JSON-LD and its SHACL shape, derive a form schema, and expose that schema via `GET /dishes/{dish_id}/schema`.
Validation is performed by `POST /dishes/{dish_id}/order` against the SHACL shapes.

## JSON-LD Structure

Planned design:
- Use a small custom vocabulary for dish forms and options.
- Each dish document contains a unique `dish_id`, human-friendly `label`, and fields.
- Fields are described by property IRIs, datatypes, and enumerated values when applicable.

Example structure (conceptual):

```json
{
  "@context": {
    "dish_id": "http://example.com/vocab/dishId",
    "label": "http://example.com/vocab/label",
    "size": "http://example.com/vocab/size",
    "filling": "http://example.com/vocab/filling"
  },
  "dish_id": "french-tacos",
  "label": "French Tacos"
}
```

## SHACL Shapes

SHACL shapes define the validation rules for each dish.
Constraints include:
- `sh:minCount` / `sh:maxCount` for required fields and cardinality
- `sh:in` for allowed enum values
- `sh:datatype` and numeric range restrictions for typed fields
- `sh:pattern` for controlled string formats

Planned examples:
- French Tacos: `size` is required, enum values are `small|medium|large`; `filling` and `sauce` are required; `notes` is optional.
- Ramen: `broth` and `noodles` are required enums; `toppings` is an optional array with max cardinality 5; `spiciness` is an integer between 0 and 5.

### Conditional Constraints

Conditional constraints are out of scope for the MVP.
The initial implementation focuses on core SHACL features that map cleanly to form fields.

## Translation to Frontend Schema

The backend translates SHACL constraints into a JSON Schema-like form schema.
This translation is intentionally generic so the frontend can:
- render any dish schema from the backend
- display labels, types, enums, and cardinality
- submit the completed payload without dish-specific logic

Mapping examples:
- `sh:datatype` → JSON Schema `type`
- `sh:in` → `enum`
- `sh:minCount = 1` → `required`
- `sh:maxCount` on arrays → `maxItems`
- numeric min/max constraints → `minimum` / `maximum`

If a SHACL constraint cannot be expressed directly, the backend will preserve the rule in metadata and still validate on submit.

## Error Response Format

Validation errors are returned in a structured problem details format with a `violations` array.
This format is not a strict standard, but it is a clear, documented contract for the frontend.

Example:

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
    }
  ]
}
```

Fields in `violations`:
- `field`: JSON pointer to the invalid field
- `code`: short validation code such as `required`, `enum`, `range`, `cardinality`
- `message`: human-readable explanation

## API Assumptions

- `GET /dishes` returns the available dishes and IDs.
- `GET /dishes/{dish_id}/schema` returns the backend-derived form schema.
- `POST /dishes/{dish_id}/order` validates the submitted payload.
- The payload body should not require a `dish` property, because `dish_id` already identifies the dish.

### Dish Discovery

The frontend selects a dish by `dish_id` and requests its schema.
This removes the need for hardcoded dish names in the frontend.

### Versioning and Deployment

JSON-LD and SHACL files are versioned in git with the backend code.
The initial backend will load shapes at startup.
Hot reload of shapes can be added later if needed, but it is not required for the MVP.

### CORS

CORS support is optional and not required for the backend design.
It can be enabled later if the frontend is hosted on a different origin.

## Example Dishes

### French Tacos
- `size`: required enum `[small, medium, large]`
- `filling`: required enum `[chicken, beef, vegetarian]`
- `sauce`: required enum `[harissa, mayo, mustard]`
- `notes`: optional string

### Ramen
- `broth`: required enum `[tonkotsu, shoyu, miso, shio]`
- `noodles`: required enum `[curly, straight, wavy]`
- `toppings`: optional array of strings, max 5 items
- `spiciness`: required integer between 0 and 5

### Custom Third Dish

The third dish should be added only by adding a JSON-LD document and a SHACL shape file to `backend/data/`.
No frontend code changes should be necessary.

## Assumptions & Limitations

- The current design assumes all dish-specific field metadata is derived from backend files.
- The frontend only consumes the schema; it does not enforce business rules independently.
- Conditional validation is not covered in the MVP.
- Shape hot reload is not implemented initially.
- The error format is a documented contract, not a standardized industry format.

## Developer Guide — SHACL → Form mapping

Purpose
- Short how-to for engineers who need to adjust or extend how SHACL shapes are translated into the frontend form schema.

Where to edit
- Primary implementation: `backend/form_generator.py`.
  - `generate_form_schema(metadata, shapes_graph)` produces the final schema returned by the API.
  - `_get_shacl_property_shapes(graph)` extracts property-shape details from a SHACL graph.
  - `_datatype_to_json_type(datatype)` maps XSD datatypes to simple JSON types.

Common mapping rules (implemented and recommended)
- `sh:datatype` → JSON `type` (string, integer, boolean). See `_datatype_to_json_type`.
- `sh:in` → `enum` (list of allowed values).
- `sh:minCount = 1` → `required: true`.
- `sh:maxCount > 1` → treat as `type: array` with `maxItems`.
- Numeric ranges (`sh:minInclusive`, `sh:maxInclusive`, `sh:minExclusive`, `sh:maxExclusive`) → `minimum` / `maximum` or custom validation metadata.
- `sh:pattern` → preserve as `pattern` (regex) in the schema or under a `validation` metadata object.

How to add a new mapping
1. Update `_get_shacl_property_shapes` to extract the SHACL predicate you need (for example, `sh:pattern` or `sh:minInclusive`) and include it in the returned shape definition dictionary.
2. Update `generate_form_schema` to read the new shape attribute and convert it into the frontend schema representation (for example, set `field_schema['pattern'] = value` or include `field_schema['minimum'] = int(value)`).
3. Preserve unfamiliar constraints in a metadata bucket so validation still happens server-side, for example:

```py
field_schema['shacl'] = shape_def  # include raw shape details for debugging/frontend hints
```

Testing and verification
- Unit tests: add small tests under `tests/` that call `DishRegistry.get_schema('your_dish')` and assert the resulting schema contains the new keys/values.
- Integration tests: validate end-to-end by calling `POST /dishes/<id>/order` with valid/invalid payloads and asserting structured violations are produced as expected.
- Manual verification: run `./start.sh`, open `http://127.0.0.1:8001`, select the dish, and confirm the field renders and client-side messages match expectations.

Best practices
- Keep translation logic simple; if a constraint cannot be expressed in the frontend schema, still validate it server-side and emit clear violation metadata.
- Add a test for every new mapping (both valid and invalid cases) and include example payloads in `tests/valid` and `tests/invalid` when appropriate.
- Avoid changing the public contract returned by `GET /dishes/{dish_id}/schema` without a versioning plan; add non-breaking metadata fields where possible.

Examples
- To support `sh:pattern`, extract `SH.pattern` in `_get_shacl_property_shapes` and set `field_schema['pattern'] = value` in `generate_form_schema`.
- To expose a numeric `minimum` from `sh:minInclusive`, add it to the shape def and map to `field_schema['minimum']`.

Notes
- The frontend is intentionally generic — prefer adding small, well-tested translation helpers rather than ad-hoc UI logic for a single dish.
- When in doubt, validate on submit: the SHACL validator is authoritative and will catch constraints that are hard to express in the form schema.

