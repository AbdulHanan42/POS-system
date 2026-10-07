from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import DeliveryZone, Order, Product, RestaurantSettings, Tenant
from app.schemas import (
    DeliveryZoneRead,
    ProductRead,
    PublicDeliveryOrderCreate,
    PublicOrderConfirmation,
)

router = APIRouter(prefix="/public", tags=["public ordering"])


def public_session(
    tenant: str = Query(default="legacy-workspace", min_length=1, max_length=100),
    session: Session = Depends(get_session),
) -> Session:
    workspace = session.exec(select(Tenant).where(Tenant.slug == tenant)).first()
    if workspace is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    session.info["tenant_id"] = workspace.id
    return session


@router.get("/menu", response_model=list[ProductRead])
def public_menu(session: Session = Depends(public_session)) -> list[Product]:
    return list(
        session.exec(
            select(Product)
            .where(Product.status == "active")
            .order_by(Product.category, Product.name)
        ).all()
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
    session: Session = Depends(public_session),
) -> PublicOrderConfirmation:
    zone = session.exec(
        select(DeliveryZone).where(
            DeliveryZone.name == order_data.deliveryZone,
            DeliveryZone.status == "active",
        )
    ).first()
    if zone is None:
        raise HTTPException(status_code=422, detail="Choose an available delivery area")

    subtotal = Decimal("0.00")
    safe_items = []
    for item in order_data.items:
        product = session.get(Product, item.productId) if item.productId is not None else None
        if product is None or product.status != "active":
            raise HTTPException(status_code=422, detail="One of the selected dishes is unavailable")
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

    settings = session.exec(select(RestaurantSettings)).first()
    tax_rate = settings.taxRate if settings else Decimal("0.1000")
    delivery_fee = zone.fee
    total = ((subtotal * (Decimal("1.00") + tax_rate)) + delivery_fee).quantize(Decimal("0.01"))
    order = Order(
        status="awaiting_payment",
        kitchenStatus="queued",
        type="Delivery",
        table="",
        customer=f"{order_data.customer} · {order_data.phone}",
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
    session.commit()
    session.refresh(order)
    return PublicOrderConfirmation(
        id=order.id,
        status=order.status,
        total=float(order.total),
        estimatedTime=zone.estimatedTime,
    )
