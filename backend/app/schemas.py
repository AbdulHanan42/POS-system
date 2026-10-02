from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PizzaPrices(BaseModel):
    small: float = Field(ge=0)
    medium: float = Field(ge=0)
    large: float = Field(ge=0)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    price: Decimal = Field(ge=0)
    status: Literal["active", "inactive"] = "active"
    image: str | None = None
    description: str | None = None
    pizzaCategory: str | None = Field(default=None, max_length=50)
    prices: PizzaPrices | None = None


class ProductRead(ProductCreate):
    id: int
    price: float

    model_config = ConfigDict(from_attributes=True)


class ProductDeleteResponse(BaseModel):
    message: str