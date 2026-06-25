# Test Cases Documentation

## Valid Payloads

### tests/valid/french-tacos-01.json
- **Dish**: French Tacos
- **Expected Result**: ✅ PASS
- **Validation**: All required fields present; values conform to allowed constraints.
- **Payload**:
  - `size`: "large" (allowed values: small, medium, large)
  - `filling`: "chicken" (allowed values: chicken, beef, vegetarian)
  - `sauce`: "harissa" (allowed values: harissa, mayo, mustard)
  - `notes`: optional field for special requests

### tests/valid/ramen-01.json
- **Dish**: Ramen
- **Expected Result**: ✅ PASS
- **Validation**: All required fields present; toppings array is valid; spiciness is within range.
- **Payload**:
  - `broth`: "tonkotsu" (allowed values: tonkotsu, shoyu, miso, shio)
  - `noodles`: "curly" (allowed values: curly, straight, wavy)
  - `toppings`: array of strings (max cardinality: 5)
  - `spiciness`: 2 (allowed range: 0-5)

## Invalid Payloads

### tests/invalid/french-tacos-missing-size.json
- **Dish**: French Tacos
- **Expected Result**: ❌ FAIL
- **Validation Error**:
  - **Field**: `/size`
  - **Code**: `required`
  - **Message**: "Field 'size' is required but was not provided."
- **Reason**: The `size` field is mandatory but absent from the submission.

### tests/invalid/ramen-invalid-broth.json
- **Dish**: Ramen
- **Expected Result**: ❌ FAIL
- **Validation Errors**:
  - **Field**: `/broth`
  - **Code**: `enum`
  - **Message**: "Value 'unknown-broth-type' is not one of the allowed values: tonkotsu, shoyu, miso, shio."
  - **Field**: `/spiciness`
  - **Code**: `range`
  - **Message**: "Value 10 exceeds maximum allowed value of 5."
- **Reason**: Broth value is not in the allowed enumeration; spiciness exceeds the valid range.

### tests/invalid/french-tacos-empty-size.json
- **Dish**: French Tacos
- **Expected Result**: ❌ FAIL
- **Validation Error**:
  - **Field**: `/size`
  - **Code**: `required`
  - **Message**: "Field 'size' must not be empty."
- **Reason**: Empty string is not accepted for a required enumerated field.

### tests/invalid/ramen-null-spiciness.json
- **Dish**: Ramen
- **Expected Result**: ❌ FAIL
- **Validation Error**:
  - **Field**: `/spiciness`
  - **Code**: `datatype`
  - **Message**: "Value null is not a valid integer."
- **Reason**: `spiciness` is required and must be a numeric value.

### tests/invalid/ramen-too-many-toppings.json
- **Dish**: Ramen
- **Expected Result**: ❌ FAIL
- **Validation Error**:
  - **Field**: `/toppings`
  - **Code**: `cardinality`
  - **Message**: "No more than 5 toppings are allowed."
- **Reason**: The toppings array exceeds the maximum cardinality of 5.

## Running Tests

Once the backend is implemented, use these payloads to:
1. Validate that SHACL shapes correctly accept valid submissions.
2. Validate that SHACL shapes correctly reject invalid submissions with appropriate error messages.
3. Ensure error responses are structured as JSON with field path, error code, and message.

Example test runner pseudocode:
```python
import json

# Load test payloads
for file in tests/valid/*.json:
    payload = json.load(file)
    result = backend.validate(payload)
    assert result.is_valid, f"Expected valid but got errors: {result.errors}"

for file in tests/invalid/*.json:
    payload = json.load(file)
    result = backend.validate(payload)
    assert not result.is_valid, f"Expected invalid but passed validation"
    assert len(result.errors) > 0, "Expected error details"
```
