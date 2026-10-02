# POS Backend

FastAPI backend for the Vue POS application. Product data is stored in PostgreSQL.

## Configure and run

From the repository root, copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL` to your PostgreSQL database, for example:

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/pos_system
```

Create the `pos_system` database in PostgreSQL if it does not exist, then install and run the backend from `backend/`:

```powershell
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe -m uvicorn main:app --reload
```

FastAPI creates the product table on startup. Interactive API docs are available at `http://127.0.0.1:8000/docs`. The Vite development server proxies `/api` requests to this backend.

## Product routes

- `GET /api/products` lists products.
- `GET /api/products/{id}` gets one product.
- `POST /api/products` creates a product.
- `PUT /api/products/{id}` replaces a product.
- `DELETE /api/products/{id}` deletes a product.

The product shape follows the Vue frontend, including optional `pizzaCategory` and `prices` (`small`, `medium`, `large`) fields.
