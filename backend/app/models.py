from decimal import Decimal

from sqlalchemy import Column, JSON, Numeric, String
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