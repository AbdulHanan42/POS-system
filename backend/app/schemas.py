from decimal import Decimal
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=240)
    isPizza: bool = False

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Category name is required")
        return value


class CategoryRead(CategoryCreate):
    id: int
    productCount: int = 0

    model_config = ConfigDict(from_attributes=True)


class CategoryDeleteResponse(BaseModel):
    message: str


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


class RestaurantTableCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    seats: int = Field(gt=0, le=50)
    status: Literal["available", "occupied", "reserved"] = "available"


class RestaurantTableRead(RestaurantTableCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StaffCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    phone: str = Field(default="", max_length=30)
    role: Literal["Administrator", "Manager", "Cashier", "Chef", "Waiter"]
    status: Literal["active", "inactive"] = "active"

    @field_validator("name")
    @classmethod
    def normalize_staff_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Staff name is required")
        return value

    @field_validator("email")
    @classmethod
    def normalize_staff_email(cls, value: str) -> str:
        value = value.strip().casefold()
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("phone")
    @classmethod
    def normalize_staff_phone(cls, value: str) -> str:
        return value.strip()


class StaffRead(StaffCreate):
    id: int
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthSignup(BaseModel):
    tenantName: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("tenantName", "name")
    @classmethod
    def normalize_auth_names(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("email")
    @classmethod
    def normalize_auth_email(cls, value: str) -> str:
        value = value.strip().casefold()
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address")
        return value


class AuthLogin(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_login_email(cls, value: str) -> str:
        return value.strip().casefold()


class AuthUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=10, max_length=128)
    role: Literal["Administrator", "Manager", "Cashier", "Chef", "Waiter"]

    @field_validator("name")
    @classmethod
    def normalize_account_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Name is required")
        return value

    @field_validator("email")
    @classmethod
    def normalize_account_email(cls, value: str) -> str:
        value = value.strip().casefold()
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address")
        return value


class AuthUserStatusUpdate(BaseModel):
    status: Literal["active", "inactive"]


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().casefold()


class PasswordResetVerify(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    otp: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().casefold()


class PasswordResetConfirm(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    otp: str = Field(min_length=6, max_length=6)
    newPassword: str = Field(min_length=10, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().casefold()


class AuthUserRead(BaseModel):
    id: int
    tenantId: int
    tenantName: str
    name: str
    email: str
    role: Literal["Administrator", "Manager", "Cashier", "Chef", "Waiter"]
    permissions: list[str]


class AuthSessionRead(BaseModel):
    accessToken: str
    tokenType: Literal["bearer"] = "bearer"
    expiresAt: datetime
    user: AuthUserRead


class AuthUserListRead(BaseModel):
    id: int
    name: str
    email: str
    role: Literal["Administrator", "Manager", "Cashier", "Chef", "Waiter"]
    status: Literal["active", "inactive"]
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class RestaurantSettingsUpdate(BaseModel):
    restaurantName: str = Field(min_length=1, max_length=120)
    email: str = Field(default="", max_length=254)
    phone: str = Field(default="", max_length=30)
    address: str = Field(default="", max_length=240)
    taxRate: Decimal = Field(ge=0, le=1)
    receiptFooter: str = Field(default="", max_length=240)

    @field_validator("restaurantName")
    @classmethod
    def normalize_restaurant_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Restaurant name is required")
        return value

    @field_validator("email")
    @classmethod
    def validate_settings_email(cls, value: str) -> str:
        value = value.strip().casefold()
        if value and (value.count("@") != 1 or "." not in value.rsplit("@", 1)[-1]):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("phone", "address", "receiptFooter")
    @classmethod
    def normalize_settings_text(cls, value: str) -> str:
        return value.strip()


class RestaurantSettingsRead(RestaurantSettingsUpdate):
    id: int
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class TableDeleteResponse(BaseModel):
    message: str


class ModifierOptionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price: float = Field(ge=0)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Modifier option name is required")
        return value


class ModifierGroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=240)
    isRequired: bool = False
    allowMultiple: bool = False
    productIds: list[int] = Field(default_factory=list)
    options: list[ModifierOptionCreate] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Modifier group name is required")
        return value

    @field_validator("options")
    @classmethod
    def ensure_unique_option_names(
        cls,
        options: list[ModifierOptionCreate],
    ) -> list[ModifierOptionCreate]:
        option_names = [option.name.casefold() for option in options]
        if len(option_names) != len(set(option_names)):
            raise ValueError("Modifier option names must be unique within a group")
        return options


class ModifierOptionRead(ModifierOptionCreate):
    pass


class ModifierGroupRead(ModifierGroupCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ModifierDeleteResponse(BaseModel):
    message: str


class InventoryStockRead(BaseModel):
    productId: int
    name: str
    category: str
    image: str | None
    unitPrice: float
    quantity: int
    reorderLevel: int
    updatedAt: datetime
    stockValue: float
    status: Literal["in_stock", "low_stock", "out_of_stock"]


class InventoryAdjustmentCreate(BaseModel):
    productId: int = Field(gt=0)
    movementType: Literal["stock_in", "stock_out"]
    quantity: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=240)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A reason is required")
        return value


class ReorderLevelUpdate(BaseModel):
    reorderLevel: int = Field(ge=0, le=100000)


class InventoryMovementRead(BaseModel):
    id: int
    productId: int
    productName: str
    movementType: Literal["stock_in", "stock_out", "sale", "refund"]
    quantity: int
    reason: str
    createdAt: datetime


class PurchaseItemCreate(BaseModel):
    productId: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unitCost: Decimal = Field(ge=0)


class PurchaseCreate(BaseModel):
    supplier: str = Field(min_length=1, max_length=120)
    items: list[PurchaseItemCreate] = Field(min_length=1)

    @field_validator("supplier")
    @classmethod
    def normalize_supplier(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Supplier is required")
        return value


class PurchaseItemRead(BaseModel):
    productId: int
    productName: str
    quantity: int
    unitCost: float
    lineTotal: float


class PurchaseRead(BaseModel):
    id: int
    supplier: str
    status: Literal["pending", "received"]
    createdAt: datetime
    total: float
    items: list[PurchaseItemRead]

    model_config = ConfigDict(from_attributes=True)


class OrderItemModifier(BaseModel):
    group: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=80)
    price: float = Field(ge=0)


class OrderItemCreate(BaseModel):
    productId: int | None = Field(default=None, gt=0)
    name: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0)
    price: Decimal = Field(ge=0)
    selectedSize: str | None = None
    modifiers: list[OrderItemModifier] = Field(default_factory=list)


class OrderCreate(BaseModel):
    createdAt: datetime | None = None
    status: Literal["paid"] = "paid"
    type: Literal["Dine in", "Takeaway", "Delivery"]
    table: str = Field(default="", max_length=80)
    customer: str = Field(min_length=1, max_length=120)
    paymentMethod: Literal["Cash", "Card", "Mobile money"]
    discount: Decimal = Field(default=Decimal("0.00"), ge=0)
    taxRate: Decimal = Field(default=Decimal("0.1000"), ge=0, le=1)
    total: Decimal = Field(ge=0)
    items: list[OrderItemCreate] = Field(min_length=1)


class KitchenOrderCreate(BaseModel):
    createdAt: datetime | None = None
    type: Literal["Dine in", "Takeaway", "Delivery"]
    table: str = Field(default="", max_length=80)
    customer: str = Field(min_length=1, max_length=120)
    discount: Decimal = Field(default=Decimal("0.00"), ge=0)
    taxRate: Decimal = Field(default=Decimal("0.1000"), ge=0, le=1)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: Literal["paid", "refunded"]


class KitchenStatusUpdate(BaseModel):
    kitchenStatus: Literal["queued", "preparing", "ready", "completed"]


class OrderPaymentCreate(BaseModel):
    paymentMethod: Literal["Cash", "Card", "Mobile money"]


class OrderItemRead(OrderItemCreate):
    price: float


class OrderRead(BaseModel):
    id: int
    createdAt: datetime
    status: Literal["awaiting_payment", "paid", "refunded"]
    kitchenStatus: Literal["queued", "preparing", "ready", "completed"]
    type: Literal["Dine in", "Takeaway", "Delivery"]
    table: str
    customer: str
    paymentMethod: str
    discount: float = 0
    taxRate: float = 0.1
    total: float
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


class DashboardSalesDay(BaseModel):
    date: str
    label: str
    total: float


class DashboardTopProduct(BaseModel):
    name: str
    quantity: int


class DashboardLowStockProduct(BaseModel):
    id: int
    name: str


class DashboardResponse(BaseModel):
    range: Literal["today", "week", "month"]
    netSales: float
    revenueChange: float
    orderCount: int
    dineInOrders: int
    averageOrder: float
    salesByDay: list[DashboardSalesDay]
    topProducts: list[DashboardTopProduct]
    lowStockProducts: list[DashboardLowStockProduct]
    recentOrders: list[OrderRead]


class SalesReportSummary(BaseModel):
    grossSales: float
    refunds: float
    netSales: float
    discounts: float
    orderCount: int
    refundCount: int
    averageOrder: float


class SalesReportDay(BaseModel):
    date: str
    label: str
    sales: float
    refunds: float
    orderCount: int


class SalesReportProduct(BaseModel):
    name: str
    quantity: int
    sales: float


class SalesReportBreakdown(BaseModel):
    name: str
    orderCount: int
    sales: float


class SalesReportTransaction(BaseModel):
    id: int
    createdAt: datetime
    customer: str
    type: str
    paymentMethod: str
    status: Literal["paid", "refunded"]
    total: float


class SalesReportRead(BaseModel):
    range: Literal["today", "week", "month", "custom"]
    startDate: str
    endDate: str
    summary: SalesReportSummary
    salesByDay: list[SalesReportDay]
    topProducts: list[SalesReportProduct]
    paymentMethods: list[SalesReportBreakdown]
    orderTypes: list[SalesReportBreakdown]
    recentOrders: list[SalesReportTransaction]