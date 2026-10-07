from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers.dashboard import router as dashboard_router
from app.routers.categories import router as categories_router
from app.routers.auth import router as auth_router
from app.routers.auth import router as auth_router
from app.routers.inventory import router as inventory_router
from app.routers.modifiers import router as modifiers_router
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.routers.purchases import router as purchases_router
from app.routers.reports import router as reports_router
from app.routers.settings import router as settings_router
from app.routers.staff import router as staff_router
from app.routers.tables import router as tables_router
from app.routers.delivery import router as delivery_router
from app.routers.public import router as public_router
from app.routers.websockets import router as websocket_router
from app.seed import seed_categories, seed_inventory, seed_products, seed_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_products()
    seed_tables()
    seed_categories()
    seed_inventory()
    yield


app = FastAPI(title="POS System API", lifespan=lifespan)
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(products_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(modifiers_router, prefix="/api")
app.include_router(tables_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(purchases_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(staff_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(delivery_router, prefix="/api")
app.include_router(public_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "POS Backend is running"}
