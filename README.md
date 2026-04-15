# ZYSOF Enterprises — Backend API

FastAPI + SQLAlchemy + PostgreSQL backend for the ZYSOF ERP system.

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your environment variables

```bash
# Copy the example file
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux

# Open .env and fill in your PostgreSQL password
```

Your `.env` should look like:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zysof_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
```

### 4. Make sure your database is running

Open pgAdmin and confirm `zysof_db` exists with all tables.
If not, run `zysof_schema.sql` first.

### 5. Start the server

```bash
uvicorn main:app --reload
```

---

## Swagger UI

Once running, open your browser and go to:

```
http://localhost:8000/docs
```

You will see the full interactive API dashboard with all endpoints.

---

## Project Structure

```
zysof_backend/
├── main.py          # FastAPI app and all API endpoints
├── models.py        # SQLAlchemy ORM models (36 tables)
├── schemas.py       # Pydantic request/response schemas
├── database.py      # PostgreSQL connection engine
├── requirements.txt # Python dependencies
├── .env.example     # Environment variable template
└── README.md        # This file
```

---

## Available Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/parts | List all parts |
| GET | /api/parts/{id} | Get a single part |
| POST | /api/parts | Create a new part |
| PATCH | /api/parts/{id} | Update a part |
| DELETE | /api/parts/{id} | Deactivate a part |
| GET | /api/customers | List all customers |
| GET | /api/customers/{id} | Get a customer |
| POST | /api/customers | Create a customer |
| PATCH | /api/customers/{id} | Update a customer |
| GET | /api/suppliers | List all suppliers |
| GET | /api/suppliers/{id} | Get a supplier |
| GET | /api/inventory | List inventory (supports low_stock_only filter) |
| GET | /api/inventory/{part_id} | Get stock for a part |
| PATCH | /api/inventory/{part_id} | Update stock level |
| GET | /api/quotations | List quotations |
| GET | /api/quotations/{id} | Get a quotation with items |
| GET | /api/invoices | List invoices |
| GET | /api/invoices/{id} | Get an invoice |
| GET | /api/website/products | Public catalogue — no prices |
| GET | /api/health | Database health check |
# zysof-backend
