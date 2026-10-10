from decimal import Decimal
import os
import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, status
from sqlmodel import Session, select

from app.auth import get_optional_current_customer
from app.database import get_session
from app.event_hub import order_events
from app.inventory import apply_inventory_movement
from app.models import Customer, DeliveryZone, InventoryStock, Order, Product, RestaurantSettings, Tenant
from app.schemas import (
    DeliveryZoneRead,
    ProductRead,
    PublicDeliveryOrderCreate,
    PublicOrderConfirmation,
    PublicOrderStatus,
    PublicSiteRead,
)

router = APIRouter(prefix="/public", tags=["public ordering"])


def public_session(
    tenant: str | None = Query(default=None, min_length=1, max_length=100),
    session: Session = Depends(get_session),
) -> Session:
    tenant_slug = (tenant or os.getenv("PUBLIC_STOREFRONT_SLUG") or "").strip()
    if not tenant_slug:
        raise HTTPException(
            status_code=503,
            detail="The public storefront is not configured. Set PUBLIC_STOREFRONT_SLUG or provide a tenant slug.",
        )

    workspace = session.exec(select(Tenant).where(Tenant.slug == tenant_slug)).first()
    if workspace is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    session.info["tenant_id"] = workspace.id
    session.info["tenant_slug"] = workspace.slug
    return session


@router.get("/menu", response_model=list[ProductRead])
def public_menu(session: Session = Depends(public_session)) -> list[Product]:
    return list(
        session.exec(
            select(Product)
            .join(InventoryStock, InventoryStock.productId == Product.id)
            .where(Product.status == "active")
            .where(InventoryStock.quantity > 0)
            .order_by(Product.category, Product.name)
        ).all()
    )


@router.get("/site", response_model=PublicSiteRead)
def public_site(session: Session = Depends(public_session)) -> PublicSiteRead:
    settings = session.exec(select(RestaurantSettings)).first()
    if settings is None:
        return PublicSiteRead(
            restaurantName="Restaurant", phone="", address="", publicDescription="",
            logoUrl="", heroImageUrl="", openingHours="", websiteEnabled=True,
            orderingOpen=True, taxRate=Decimal("0.1000"),
            tenantSlug=session.info["tenant_slug"],
        )
    return PublicSiteRead(
        restaurantName=settings.restaurantName,
        phone=settings.phone,
        address=settings.address,
        publicDescription=settings.publicDescription,
        logoUrl=settings.logoUrl,
        heroImageUrl=settings.heroImageUrl,
        openingHours=settings.openingHours,
        websiteEnabled=settings.websiteEnabled,
        orderingOpen=settings.orderingOpen,
        taxRate=settings.taxRate,
        tenantSlug=session.info["tenant_slug"],
    )


@router.get("/delivery-zones", response_model=list[DeliveryZoneRead])
def public_delivery_zones(session: Session = Depends(public_session)) -> list[DeliveryZone]:
    return list(
        session.exec(
            select(DeliveryZone)
            .where(DeliveryZone.status == "active")
            .order_by(DeliveryZone.name)
        ).all()
    )


@router.post(
    "/orders",
    response_model=PublicOrderConfirmation,
    status_code=status.HTTP_201_CREATED,
)
def create_public_order(
    order_data: PublicDeliveryOrderCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(public_session),
    customer: Customer | None = Depends(get_optional_current_customer),
) -> PublicOrderConfirmation:
    zone = session.exec(
        select(DeliveryZone).where(
            DeliveryZone.name == order_data.deliveryZone,
            DeliveryZone.status == "active",
        )
    ).first()
    if zone is None:
        raise HTTPException(status_code=422, detail="Choose an available delivery area")

    settings = session.exec(select(RestaurantSettings)).first()
    if settings and (not settings.websiteEnabled or not settings.orderingOpen):
        raise HTTPException(status_code=409, detail="Online ordering is currently unavailable")

    subtotal = Decimal("0.00")
    safe_items = []
    products: dict[int, Product] = {}
    ordered_quantities: dict[int, int] = {}
    for item in order_data.items:
        product = session.get(Product, item.productId) if item.productId is not None else None
        if product is None or product.status != "active":
            raise HTTPException(status_code=422, detail="One of the selected dishes is unavailable")
        products[product.id] = product
        ordered_quantities[product.id] = ordered_quantities.get(product.id, 0) + item.quantity
        price = product.price
        selected_size = item.selectedSize
        if product.prices:
            size_key = (selected_size or "medium").lower()
            if size_key not in product.prices:
                raise HTTPException(status_code=422, detail=f"Choose a valid size for {product.name}")
            price = Decimal(str(product.prices[size_key]))
            selected_size = size_key.title()
        subtotal += price * item.quantity
        safe_items.append({
            "productId": product.id,
            "name": product.name,
            "quantity": item.quantity,
            "price": float(price),
            "selectedSize": selected_size,
            "modifiers": [],
        })

    if subtotal < zone.minOrderAmount:
        raise HTTPException(
            status_code=422,
            detail=f"This area requires a minimum order of {zone.minOrderAmount:.2f}",
        )

    tax_rate = settings.taxRate if settings else Decimal("0.1000")
    delivery_fee = zone.fee
    total = ((subtotal * (Decimal("1.00") + tax_rate)) + delivery_fee).quantize(Decimal("0.01"))
    order = Order(
        status="awaiting_payment",
        kitchenStatus="queued",
        type="Delivery",
        table="",
        customer=f"{order_data.customer} · {order_data.phone}",
        customerPhone=order_data.phone,
        customerId=customer.id if customer else None,
        source="website",
        publicTrackingToken=secrets.token_urlsafe(32),
        paymentMethod="Cash",
        discount=Decimal("0.00"),
        taxRate=tax_rate,
        total=total,
        items=safe_items,
        deliveryAddress=order_data.deliveryAddress,
        deliveryZone=zone.name,
        deliveryFee=delivery_fee,
        deliveryStatus="pending",
        deliveryNotes=order_data.deliveryNotes,
    )
    session.add(order)
    session.flush()
    for product_id, quantity in ordered_quantities.items():
        apply_inventory_movement(
            session,
            products[product_id],
            "sale",
            quantity,
            f"Website order #{order.id}",
        )
    session.commit()
    session.refresh(order)
    background_tasks.add_task(order_events.order_created, order.tenantId, order.id, order.source)
    return PublicOrderConfirmation(
        id=order.id,
        status=order.status,
        total=float(order.total),
        estimatedTime=zone.estimatedTime,
        trackingToken=order.publicTrackingToken,
    )


@router.get("/orders/{order_id}/status", response_model=PublicOrderStatus)
def public_order_status(
    order_id: int,
    token: str = Header(alias="X-Order-Tracking-Token", min_length=32, max_length=64),
    session: Session = Depends(public_session),
) -> PublicOrderStatus:
    order = session.exec(select(Order).where(Order.id == order_id)).first()
    if order is None or order.publicTrackingToken is None or not secrets.compare_digest(order.publicTrackingToken, token):
        raise HTTPException(status_code=404, detail="Order not found")
    return PublicOrderStatus(
        id=order.id,
        status=order.status,
        kitchenStatus=order.kitchenStatus,
        deliveryStatus=order.deliveryStatus,
        total=float(order.total),
        estimatedDeliveryTime=order.estimatedDeliveryTime,
    )
