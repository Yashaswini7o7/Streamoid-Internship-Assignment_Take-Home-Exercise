# Streamoid-Internship-Assignment_Take-Home-Exercise

A small backend service to upload product CSVs, validate rows, store valid products in SQLite, list products with pagination and search/filter products.


## Features
- `POST /upload` — upload CSV file, validate and store valid rows
- `GET /products` — list products with pagination (`page`, `limit`)
- `GET /products/search` — search/filter by `brand`, `color`, `minPrice`, `maxPrice`


## Tech
- Python 3.10+
- FastAPI (for clean API design)
- SQLAlchemy + SQLite
- Uvicorn for running
- Pytest for unit tests
- Dockerfile included


## Quickstart (local)

```markdown

1. Create a virtualenv and install:


```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


2. Run the app:


```bash`
uvicorn app:app --reload --port 8000`


3. Open docs at http://localhost:8000/docs (Swagger UI)
