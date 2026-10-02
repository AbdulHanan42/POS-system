from decimal import Decimal
from datetime import datetime
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


class OrderItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0)
    price: Decimal = Field(ge=0)
    selectedSize: str | None = None


class OrderCreate(BaseModel):
    createdAt: datetime | None = None
    status: Literal["paid"] = "paid"
    type: Literal["Dine in", "Takeaway", "Delivery"]
    table: str = Field(default="", max_length=80)
    customer: str = Field(min_length=1, max_length=120)
    paymentMethod: Literal["Cash", "Card", "Mobile money"]
    total: Decimal = Field(ge=0)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: Literal["paid", "refunded"]


class OrderItemRead(OrderItemCreate):
    price: float


class OrderRead(BaseModel):
    id: int
    createdAt: datetime
    status: Literal["paid", "refunded"]
    type: Literal["Dine in", "Takeaway", "Delivery"]
    table: str
    customer: str
    paymentMethod: str
    total: float
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)