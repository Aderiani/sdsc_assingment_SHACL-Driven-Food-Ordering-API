from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from .schema_loader import DishRegistry, DishNotFoundError
from .validation import ValidationErrorResponse

app = FastAPI(title="SHACL-driven Dish Ordering API")
registry = DishRegistry("backend/data")


@app.get("/dishes")
def list_dishes():
    return registry.list_dishes()


@app.get("/dishes/{dish_id}/schema")
def get_dish_schema(dish_id: str):
    try:
        return registry.get_schema(dish_id)
    except DishNotFoundError:
        raise HTTPException(status_code=404, detail="Dish not found")


@app.post("/dishes/{dish_id}/order")
async def submit_order(dish_id: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        validation_result = registry.validate_order(dish_id, payload)
    except DishNotFoundError:
        raise HTTPException(status_code=404, detail="Dish not found")

    if validation_result.valid:
        return {"valid": True}
    error_response = ValidationErrorResponse.from_validation_result(validation_result)
    return JSONResponse(
        status_code=400,
        content=asdict(error_response),
    )
