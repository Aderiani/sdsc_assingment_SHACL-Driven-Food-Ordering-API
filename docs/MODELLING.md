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
