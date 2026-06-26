# Backend Setup

This project uses a Python FastAPI backend to load dish definitions from `backend/data/`, generate form schema from SHACL shapes, and validate submitted orders.

## Setup

1. Install Python 3.14 venv support:
   - Debian/Ubuntu: `sudo apt install python3.14-venv`
2. Create a virtual environment:
   - `python3 -m venv .venv`
3. Activate the environment:
   - `source .venv/bin/activate`
4. Install dependencies:
   - `pip install -r requirements.txt`

## Run

Start the API server:

```bash
python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

## Endpoints

- `GET /dishes`
- `GET /dishes/{dish_id}/schema`
- `POST /dishes/{dish_id}/order`

## Tests

Run the backend tests with:

```bash
python3 -m pytest
```
