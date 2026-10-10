# Restaurant Customer Website

Standalone Vue 3 customer storefront. The existing POS and this app use the same FastAPI API and PostgreSQL database; this project contains no POS/admin screens.

## Run

Start the FastAPI backend on `http://127.0.0.1:8000`, then run:

```sh
npm install
npm run dev
```

The dev server runs on `http://localhost:5174` and proxies `/api` and WebSocket traffic to FastAPI. Set `VITE_RESTAURANT_SLUG` in `.env.local` to choose the public default restaurant for direct visits. The POS preview link supplies `?tenant=<workspace-slug>` and overrides that default. The public slug is not an admin credential; never pass a POS access token to the customer site.

Set `VITE_API_BASE_URL` only when the deployed API is on a different origin. Configure that origin in the backend CORS policy for REST requests.

## Build

```sh
npm run build
npm run preview
```

Public menu, delivery areas, restaurant settings, order creation, and order status use the existing `/api/public` endpoints. The backend recalculates prices and validates availability; customer tracking uses an unguessable per-order token. WebSocket events improve update speed, with REST polling as a fallback.
