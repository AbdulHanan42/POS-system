from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint
from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=120)
    slug: str = Field(max_length=100, unique=True, index=True)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )


class UserAccount(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, index=True)
    )
    name: str = Field(max_length=120)
    email: str = Field(max_length=254, unique=True, index=True)
    passwordHash: str = Field(
        sa_column=Column("password_hash", String(200), nullable=False),
    )
    role: str = Field(max_length=40, index=True)
    status: str = Field(default="active", max_length=20, index=True)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )


class AuthSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    userId: int = Field(
        sa_column=Column("user_id", Integer, ForeignKey("useraccount.id"), nullable=False, index=True)
    )
    tokenHash: str = Field(
        sa_column=Column("token_hash", String(64), nullable=False, unique=True, index=True),
    )
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )
    expiresAt: datetime = Field(
        sa_column=Column("expires_at", DateTime(timezone=True), nullable=False, index=True),
    )
    revokedAt: datetime | None = Field(
        default=None,
        sa_column=Column("revoked_at", DateTime(timezone=True), nullable=True),
    )


class Category(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_category_tenant_name"),)

    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    name: str = Field(
        sa_column=Column(String(80), nullable=False, index=True)
    )
    description: str = Field(default="", max_length=240)
    isPizza: bool = Field(
        default=False,
        sa_column=Column("is_pizza", Boolean, nullable=False, default=False),
    )


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
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
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    name: str = Field(index=True, max_length=80)
    seats: int = Field(gt=0)
    status: str = Field(default="available", max_length=20, index=True)


class StaffMember(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    name: str = Field(max_length=120, index=True)
    email: str = Field(max_length=254, unique=True, index=True)
    phone: str = Field(default="", max_length=30)
    role: str = Field(max_length=40, index=True)
    status: str = Field(default="active", max_length=20, index=True)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )


class RestaurantSettings(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("tenant_id", name="uq_restaurantsettings_tenant_id"),)

    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    restaurantName: str = Field(default="Restaurant POS", max_length=120)
    email: str = Field(default="", max_length=254)
    phone: str = Field(default="", max_length=30)
    address: str = Field(default="", max_length=240)
    taxRate: Decimal = Field(
        default=Decimal("0.1000"),
        sa_column=Column(Numeric(5, 4), nullable=False, default=Decimal("0.1000")),
    )
    receiptFooter: str = Field(default="", max_length=240)
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("updated_at", DateTime(timezone=True), nullable=False),
    )


class ModifierGroup(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_modifiergroup_tenant_name"),)

    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    name: str = Field(
        sa_column=Column(String(80), nullable=False, index=True)
    )
    description: str = Field(default="", max_length=240)
    isRequired: bool = Field(
        default=False,
        sa_column=Column("is_required", Boolean, nullable=False, default=False),
    )
    allowMultiple: bool = Field(
        default=False,
        sa_column=Column("allow_multiple", Boolean, nullable=False, default=False),
    )
    productIds: list[int] = Field(
        default_factory=list,
        sa_column=Column("product_ids", JSON, nullable=False, default=list),
    )
    options: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, default=list),
    )


class InventoryStock(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    productId: int = Field(index=True, unique=True)
    quantity: int = Field(default=0, ge=0)
    reorderLevel: int = Field(default=5, ge=0)
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("updated_at", DateTime(timezone=True), nullable=False),
    )


class InventoryMovement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    productId: int = Field(index=True)
    movementType: str = Field(max_length=20, index=True)
    quantity: int = Field(gt=0)
    reason: str = Field(max_length=240)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )


class Purchase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    supplier: str = Field(max_length=120, index=True)
    status: str = Field(default="pending", max_length=20, index=True)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )
    total: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    items: list[dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=False),
    )


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenantId: int = Field(
        sa_column=Column("tenant_id", Integer, ForeignKey("tenant.id"), nullable=False, default=1, index=True)
    )
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False),
    )
    status: str = Field(default="paid", max_length=20, index=True)
    kitchenStatus: str = Field(
        default="queued",
        sa_column=Column("kitchen_status", String(20), nullable=False, default="queued"),
    )
    type: str = Field(max_length=30)
    table: str = Field(
        default="",
        sa_column=Column("table_name", String(80), nullable=False, default=""),
    )
    customer: str = Field(max_length=120)
    paymentMethod: str = Field(
        sa_column=Column("payment_method", String(40), nullable=False),
    )
    discount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=Decimal("0.00")),
    )
    taxRate: Decimal = Field(
        default=Decimal("0.1000"),
        sa_column=Column(
            "tax_rate",
            Numeric(5, 4),
            nullable=False,
            default=Decimal("0.1000"),
        ),
    )
    total: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    items: list[dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=False),
    )