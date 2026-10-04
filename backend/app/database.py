import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Copy backend/.env.example to backend/.env "
        "and configure your PostgreSQL credentials."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    from app.models import (
        Category,
        InventoryMovement,
        InventoryStock,
        ModifierGroup,
        Order,
        Purchase,
        Product,
        RestaurantTable,
    )

    SQLModel.metadata.create_all(engine)
    with engine.begin() as connection:
        columns = {
            column["name"]
            for column in inspect(connection).get_columns(Order.__tablename__)
        }
        if "kitchen_status" not in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{Order.__tablename__}" '
                    "ADD COLUMN kitchen_status VARCHAR(20) NOT NULL DEFAULT 'queued'"
                )
            )
        if "discount" not in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{Order.__tablename__}" '
                    "ADD COLUMN discount NUMERIC(10, 2) NOT NULL DEFAULT 0"
                )
            )