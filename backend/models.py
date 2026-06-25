from pydantic import BaseModel
from typing import Any, Dict, List


class ValidationError(BaseModel):
    field: str
    constraint: str
    message: str


class ValidationResponse(BaseModel):
    valid: bool
    errors: List[ValidationError]


class DishSchema(BaseModel):
    id: str
    title: str
    fields: List[Dict[str, Any]]
