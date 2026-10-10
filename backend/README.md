# POS Backend

FastAPI backend for the Vue POS application. Product data is stored in PostgreSQL.

## Configure and run

From the repository root, copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL` to your PostgreSQL database, for example:

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/pos_system
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=mailer@example.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=orders@example.com
SMTP_USE_SSL=false
CUSTOMER_SITE_URL=http://localhost:5174
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=orders@example.com
```

Set your SMTP server credentials and sender in `backend/.env`. Port 587 uses
STARTTLS; port 465 uses implicit TLS by default. SMTP is tried first. If SMTP is
unavailable, Resend is used when its API key and verified sender are configured.
Customer registration sends a six-digit code that expires after 10 minutes; codes
can be resent once per minute and verification is limited to five attempts. The
account and sign-in session are created only after the code is verified, then a
confirmation email is sent.

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
