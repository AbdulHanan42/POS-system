# POS System — Claude Project Instructions

## 1. Project Overview

This is a full-stack Restaurant Point of Sale (POS) System.

The project has two main parts:

- Frontend: Vue 3 + Vite
- Backend: FastAPI + SQLModel + PostgreSQL

The frontend communicates with the FastAPI backend through `/api` endpoints.

The frontend Vite development server proxies `/api` requests to:

```text
http://127.0.0.1:8000
```

The backend API is therefore the source of truth for persistent application data.

Do NOT replace the backend with mock data when implementing features unless explicitly requested.

---

# 2. Frontend Stack

Use the existing frontend technologies. Do not introduce another framework unnecessarily.

Main technologies:

- Vue 3
- Composition API
- JavaScript
- Vite
- Vue Router
- Pinia
- Tailwind CSS v4
- Lucide Vue icons
- Vitest
- Vue Test Utils
- Playwright
- ESLint
- Oxlint

The project uses Vue 3.5.x and Pinia 4.x.

Use:

```vue
<script setup>
```

and the Composition API for Vue components.

Do NOT use the Vue Options API unless an existing component already requires it and changing it would create unnecessary risk.

---

# 3. Backend Stack

Backend technologies:

- Python
- FastAPI
- SQLModel
- PostgreSQL
- Psycopg
- Resend for password-reset email
- Uvicorn for development server

Backend entry point:

```text
backend/main.py
```

Backend application code:

```text
backend/app/
```

API routers are located at:

```text
backend/app/routers/
```

Database models are located in:

```text
backend/app/models.py
```

Pydantic request/response schemas are located in:

```text
backend/app/schemas.py
```

Database/session configuration:

```text
backend/app/database.py
```

Authentication and authorization:

```text
backend/app/auth.py
```

---

# 4. Important Project Architecture

Follow this general frontend flow:

```text
View
  ↓
Component
  ↓
Pinia Store
  ↓
Service
  ↓
API helper
  ↓
FastAPI Router
  ↓
Schema
  ↓
Database Model
  ↓
PostgreSQL
```

For example:

```text
Products.vue
    ↓
ProductTable.vue / ProductForm.vue
    ↓
product.js store
    ↓
productService.js
    ↓
api.js
    ↓
/api/products
    ↓
backend/app/routers/products.py
    ↓
schemas.py
    ↓
models.py
    ↓
PostgreSQL
```

Respect this architecture.

Do not put API calls directly inside UI components when an existing service/store architecture can be used.

---

# 5. Frontend Folder Responsibilities

## src/components/

Reusable UI components.

### components/common/

Generic reusable components:

- BaseBadge.vue
- BaseButton.vue
- BaseInput.vue
- BaseLoader.vue
- BaseModal.vue
- BasePagination.vue
- BaseTable.vue

Before creating a new generic UI component, check whether one of these can be reused.

---

## components/customers/

Customer-specific reusable components.

---

## components/dashboard/

Dashboard-specific components:

- statistics
- charts
- recent orders
- top products

---

## components/kitchen/

Kitchen order components.

---

## components/layout/

Application layout components:

- Header
- Sidebar
- Footer
- Breadcrumb

---

## components/pos/

POS-specific components:

- Cart
- CartItem
- CategoryTabs
- OrderSummary
- PaymentModal
- ReceiptModal
- ProductCard
- ProductGrid
- SearchProduct

---

## components/products/

Product management components.

---

## components/tables/

Restaurant table components.

---

# 6. Views

Views represent complete application pages.

Important areas:

```text
src/views/auth/
src/views/customers/
src/views/dashboard/
src/views/inventory/
src/views/kitchen/
src/views/menu/
src/views/orders/
src/views/pos/
src/views/purchases/
src/views/reports/
src/views/settings/
src/views/staff/
src/views/tables/
```

Do not turn every piece of UI into a view.

Use components for reusable page sections.

---

# 7. Layouts

Existing layouts:

```text
src/layouts/AuthLayout.vue
src/layouts/DefaultLayout.vue
src/layouts/PosLayout.vue
```

Use the appropriate existing layout instead of creating a new layout unnecessarily.

---

# 8. Router

Router:

```text
src/router/index.js
```

When adding a new page:

1. Create the view.
2. Register the route.
3. Apply the appropriate layout.
4. Check authentication/permission requirements.
5. Add navigation if necessary.

Do not forget route-level access control when adding protected functionality.

---

# 9. Pinia Stores

Stores are located in:

```text
src/stores/
```

Existing stores include:

```text
auth.js
cart.js
category.js
counter.js
customer.js
inventory.js
modifier.js
order.js
pos.js
product.js
purchase.js
settings.js
staff.js
table.js
```

Use Pinia for shared application state.

Do not duplicate the same state across multiple unrelated components.

Before creating a new store, check whether an existing store already handles the required state.

---

# 10. Services

API-related frontend logic belongs in:

```text
src/services/
```

Existing services:

```text
api.js
authService.js
categoryService.js
customerService.js
dashboardService.js
inventoryService.js
modifierService.js
orderService.js
productService.js
purchaseService.js
reportService.js
settingsService.js
staffService.js
tableService.js
```

When implementing backend communication:

- Prefer the existing service.
- Reuse `api.js`.
- Do not create duplicate API helpers.
- Do not put large API implementations directly inside `.vue` files.

---

# 11. Fetch / API Rule

Use the project's existing API abstraction.

Prefer:

```javascript
async/await
```

and the existing fetch-based API architecture.

Do NOT introduce Axios unless explicitly requested.

Do NOT create a second HTTP client.

Before implementing an API request, inspect:

```text
src/services/api.js
```

and the relevant service/store.

---

# 12. Composables

Existing composables:

```text
src/composables/useFetch.js
src/composables/useModal.js
src/composables/usePagination.js
src/composables/usePermissions.js
src/composables/useSearch.js
```

Reuse these where appropriate.

Especially check:

```text
usePermissions.js
```

before implementing permission-based UI.

---

# 13. Authentication

Authentication is implemented by the FastAPI backend.

Important backend authentication files:

```text
backend/app/auth.py
backend/app/routers/auth.py
```

The backend uses bearer authentication with server-side sessions.

Important concepts:

- User
- Tenant
- Role
- Permissions
- Auth session
- Password reset
- OTP

Do not replace the existing authentication system with JWT unless explicitly requested.

Do not change authentication behavior casually.

---

# 14. Roles

The backend currently defines these roles:

```text
Administrator
Manager
Cashier
Chef
Waiter
```

Permissions are role-based.

Current conceptual permissions include areas such as:

```text
pos:use
catalog:read
orders:read
orders:create
orders:payment
inventory:read
customers:manage
kitchen:read
kitchen:update
tables:read
tables:update
```

Administrator and Manager currently have wildcard permissions.

Always inspect the actual backend permission definitions before modifying authorization logic.

---

# 15. Multi-Tenant Architecture

The application has a tenant/workspace concept.

Important models include:

```text
Tenant
UserAccount
AuthSession
```

Most business data is tenant-scoped.

The backend applies tenant filtering automatically through the database session.

Do NOT remove tenant filtering.

Do NOT assume all users belong to a single global restaurant.

When adding a new tenant-specific model:

- Include `tenantId`.
- Follow the existing database/session tenant-scoping pattern.
- Make sure queries cannot leak data between tenants.

Security is more important than convenience.

---

# 16. Main Business Modules

The application contains these major modules:

### Authentication

```text
Login
Signup
Forgot Password
OTP Verification
Reset Password
```

### Dashboard

```text
Statistics
Sales Chart
Recent Orders
Top Products
```

### POS

```text
Products
Categories
Cart
Order Summary
Payment
Receipt
Customers
Tables
```

### Products/Menu

```text
Products
Categories
Modifiers
Product Details
Create Product
Edit Product
```

### Inventory

```text
Inventory
Stock In
Stock History
Stock Adjustment
Reorder Level
```

### Orders

```text
Orders
Order Details
Order Status
Kitchen Status
Payments
```

### Kitchen

```text
Kitchen Orders
Queued
Preparing
Ready
Completed
```

### Purchases

```text
Purchases
Create Purchase
Purchase Items
Suppliers
```

### Reports

```text
Sales Report
Product Report
Payment Report
Profit Report
```

### Staff

```text
Staff
Roles
Permissions
```

### Tables

```text
Restaurant Tables
Available
Occupied
Reserved
```

### Settings

```text
General Settings
Restaurant Settings
Tax Settings
```

---

# 17. Important Database Models

Existing backend models include:

```text
Tenant
UserAccount
AuthSession
PasswordReset
Category
Product
RestaurantTable
StaffMember
RestaurantSettings
ModifierGroup
InventoryStock
InventoryMovement
Purchase
Order
```

Before changing database behavior, inspect:

```text
backend/app/models.py
backend/app/schemas.py
backend/app/database.py
```

Do not assume fields or relationships that are not present in the code.

---

# 18. Product Model

Products currently contain concepts such as:

```text
id
tenantId
name
category
price
status
image
description
pizzaCategory
prices
```

Pizza pricing can include:

```text
small
medium
large
```

When modifying products, inspect the existing frontend product components, store, service, backend schema, router, and model before making changes.

---

# 19. Inventory

Inventory uses:

```text
InventoryStock
InventoryMovement
```

Inventory movement types include:

```text
stock_in
stock_out
sale
refund
```

Stock cannot go below zero during stock-out/sale operations.

The backend contains centralized inventory movement logic.

Do not implement a second independent stock calculation in the frontend.

The backend should remain the source of truth for stock quantities.

---

# 20. Orders

Orders contain concepts including:

```text
createdAt
status
kitchenStatus
type
table
customer
paymentMethod
discount
taxRate
total
items
```

Order types:

```text
Dine in
Takeaway
Delivery
```

Kitchen statuses:

```text
queued
preparing
ready
completed
```

Payment methods include:

```text
Cash
Card
Mobile money
```

Do not change these values without checking all frontend/backend consumers.

---

# 21. Modifiers

Modifier groups support:

```text
name
description
isRequired
allowMultiple
productIds
options
```

Modifier options contain:

```text
name
price
```

Option names must be unique within a modifier group.

---

# 22. Restaurant Tables

Tables have:

```text
name
seats
status
```

Current statuses:

```text
available
occupied
reserved
```

Do not introduce different status values without checking existing frontend/backend logic.

---

# 23. Styling Rules

The project uses:

```text
Tailwind CSS v4
```

Prefer existing Tailwind styling patterns.

Do not introduce another CSS framework.

Do not install Bootstrap, Vuetify, Material UI, or another component framework unless explicitly requested.

Reuse existing CSS variables/styles when appropriate:

```text
src/assets/styles/main.css
src/assets/styles/variables.css
```

Keep UI consistent with the existing POS design.

---

# 24. Icons

The project uses:

```text
lucide-vue-next
```

Prefer existing Lucide icons instead of adding another icon library.

---

# 25. Validation

Frontend validation utilities exist in:

```text
src/utils/validation.js
src/utils/productValidation.js
```

Backend validation exists in:

```text
backend/app/schemas.py
```

Always respect backend validation.

Frontend validation should improve UX but must not be treated as the only security validation.

---

# 26. Testing

The project uses:

### Unit tests

```text
Vitest
Vue Test Utils
```

Tests are located in:

```text
src/__tests__/
```

and alongside relevant views.

### E2E tests

```text
Playwright
```

located in:

```text
e2e/
```

When changing important business functionality, check existing tests and update/add tests where appropriate.

Do not delete tests simply because they fail after a change.

Investigate the reason first.

---

# 27. Existing Configuration

Frontend development:

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
```

Unit tests:

```bash
npm run test:unit
```

E2E tests:

```bash
npm run test:e2e
```

Lint:

```bash
npm run lint
```

Backend dependencies are installed from:

```text
backend/requirements.txt
```

Backend API runs on:

```text
http://127.0.0.1:8000
```

Swagger/OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 28. Important Development Rules

Before changing code:

1. Inspect the existing implementation.
2. Understand how the feature currently works.
3. Identify frontend view/component/store/service.
4. Identify corresponding backend router/schema/model.
5. Make the smallest clean change necessary.
6. Reuse existing utilities/components.
7. Preserve existing functionality.
8. Check permissions/authentication.
9. Check tenant isolation.
10. Run relevant tests/build/lint when practical.

Do not rewrite entire modules when a focused change is sufficient.

---

# 29. Do Not Make Unnecessary Changes

Do NOT:

- Rewrite the architecture without permission.
- Replace Vue with React.
- Replace FastAPI with another backend.
- Replace PostgreSQL.
- Replace Pinia.
- Replace Vue Router.
- Add Axios unnecessarily.
- Add another CSS framework.
- Remove existing components just because you prefer another approach.
- Rename large numbers of files without a clear reason.
- Change API contracts without checking all consumers.
- Remove authentication/authorization.
- Remove tenant isolation.
- Replace backend data with hardcoded frontend data.

---

# 30. When Fixing Bugs

When asked to fix a bug:

First determine:

```text
Where does the bug originate?
```

Check the full flow:

```text
UI
→ component
→ store
→ service
→ API
→ FastAPI router
→ schema
→ model/database
```

Fix the root cause rather than hiding the problem in the UI.

Do not modify unrelated files.

After fixing, explain:

1. What caused the problem.
2. What was changed.
3. Which files were changed.
4. How the fix works.
5. How it can be tested.

---

# 31. When Adding a New Feature

Follow this process:

### Step 1 — Understand existing architecture

Search the repository for similar functionality.

### Step 2 — Frontend

Determine:

```text
View
Component
Store
Service
Router
Composable
Utility
```

### Step 3 — Backend

Determine:

```text
Router
Schema
Model
Database logic
Authentication
Permission
```

### Step 4 — API contract

Make sure frontend request/response structures match backend schemas.

### Step 5 — Implement

Make the smallest maintainable change.

### Step 6 — Test

Run the relevant unit/E2E tests and build.

---

# 32. Code Style

Prefer simple, readable code.

Use:

```javascript
const
let
async/await
optional chaining
destructuring
```

where appropriate.

Avoid unnecessary abstractions.

Avoid deeply nested logic.

Use meaningful variable names.

Keep Vue components focused.

If a component becomes too large, consider extracting reusable components or composables.

---

# 33. Important Instruction About Existing Code

The existing repository is the source of truth.

If this document conflicts with actual code, inspect the code and follow the actual implementation rather than assuming this document is correct.

Never invent an API endpoint, database field, store property, permission, route, or component API.

Search the repository before making assumptions.

---

# 34. Claude Behavior

When working on this project:

- Act as a senior full-stack engineer.
- Understand the existing architecture before editing.
- Prefer minimal, safe, maintainable changes.
- Preserve existing functionality.
- Follow existing naming conventions.
- Reuse existing components and utilities.
- Keep frontend and backend contracts synchronized.
- Consider security and tenant isolation.
- Consider loading, error, empty, and success states.
- Consider permissions for protected operations.
- Consider responsive UI.
- Do not blindly generate code without inspecting relevant files.

When I ask for a feature or bug fix, do not immediately rewrite the project.

First inspect the relevant files and determine the correct implementation path.

If multiple approaches are possible, choose the approach that best fits the existing architecture.

---

# 35. Project Directory

The important project structure is:

```text
abdulhanan42-pos-system/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── auth.py
│       ├── database.py
│       ├── email.py
│       ├── inventory.py
│       ├── models.py
│       ├── schemas.py
│       ├── seed.py
│       └── routers/
│
├── e2e/
│
└── src/
    ├── components/
    ├── composables/
    ├── data/
    ├── layouts/
    ├── router/
    ├── services/
    ├── stores/
    ├── utils/
    └── views/
```

This is an existing production-style POS architecture. Maintain the separation of concerns.

---

# 36. Security Rules

Never expose secrets in frontend code.

Never commit:

```text
.env
API keys
database passwords
private credentials
```

The backend `.env` contains sensitive configuration.

If a secret appears in source code or an example file, do not copy or expose it unnecessarily.

For password reset/email functionality, keep credentials server-side.

---

# 37. Final Rule

Before writing code, understand the existing code.

Before changing an API, inspect its frontend consumers.

Before changing a database model, inspect its schemas, routers, services, stores, and views.

Before changing permissions, inspect both frontend permission checks and backend authorization.

Before adding a new abstraction, check whether an existing abstraction already solves the problem.

The goal is not simply to make the requested code work.

The goal is to make it work **inside the existing POS architecture without breaking existing functionality.**