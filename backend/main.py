from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers.dashboard import router as dashboard_router
from app.routers.categories import router as categories_router
from app.routers.modifiers import router as modifiers_router
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.routers.tables import router as tables_router
from app.seed import seed_categories, seed_products, seed_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_products()
    seed_tables()
    seed_categories()
    yield


app = FastAPI(title="POS System API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(modifiers_router, prefix="/api")
app.include_router(tables_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "POS Backend is running"}