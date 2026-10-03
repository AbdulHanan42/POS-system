from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import Column, DateTime, JSON, Numeric, String
from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=120)
    category: str = Field(index=True, max_length=80)
    price: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    status: str = Field(default="active", max_length=20)
    image: str | None = Field(default=None)
    description: str | None = Field(default=None)
    pizzaCategory: str | None = Field(
        default=None,
        sa_column=Column("pizza_category", String(50), nullable=True),
    )
    prices: dict[str, float] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )


class RestaurantTable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=80)
    seats: int = Field(gt=0)
    status: str = Field(default="available", max_length=20, index=True)


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )
    status: str = Field(default="paid", max_length=20, index=True)
    type: str = Field(max_length=30)
    table: str = Field(
        default="",
        sa_column=Column("table_name", String(80), nullable=False, default=""),
    )
    customer: str = Field(max_length=120)
    paymentMethod: str = Field(
        sa_column=Column("payment_method", String(40), nullable=False),
    )
    total: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    items: list[dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=False),
    )