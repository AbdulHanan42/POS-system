from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.inventory import apply_inventory_movement, get_or_create_stock
from app.models import Order, Product
from app.schemas import (
    KitchenOrderCreate,
    KitchenStatusUpdate,
    OrderCreate,
    OrderPaymentCreate,
    OrderRead,
    OrderStatusUpdate,
)

router = APIRouter(prefix="/orders", tags=["orders"])
KITCHEN_ORDER_STATUSES = {"awaiting_payment", "paid"}
KITCHEN_TRANSITIONS = {
    "queued": "preparing",
    "preparing": "ready",
    "ready": "completed",
}


@router.get("", response_model=list[OrderRead])
def list_orders(session: Session = Depends(get_session)) -> list[Order]:
    return list(session.exec(select(Order).order_by(Order.createdAt.desc())).all())


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session)) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
) -> Order:
    ordered_quantities: dict[int, int] = {}
    products: dict[int, Product] = {}
    stocks = {}
    for item in order_data.items:
        if item.productId is None:
            continue
        product = session.get(Product, item.productId)
        if product is None:
            raise HTTPException(status_code=404, detail="Ordered product not found")
        products[item.productId] = product
        ordered_quantities[item.productId] = ordered_quantities.get(item.productId, 0) + item.quantity
        stocks[item.productId] = get_or_create_stock(session, item.productId)

    for product_id, quantity in ordered_quantities.items():
        if stocks[product_id].quantity < quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Not enough stock for {products[product_id].name} ({stocks[product_id].quantity} available)",
            )

    order_values = order_data.model_dump(exclude={"createdAt", "items"})
    order_values["createdAt"] = order_data.createdAt or datetime.now(timezone.utc)
    order_values["total"] = Decimal(order_data.total)
    order_values["items"] = []
    for item in order_data.items:
        item_values = item.model_dump()
        item_values["price"] = float(item.price)
        order_values["items"].append(item_values)

    order = Order(**order_values)
    session.add(order)
    session.flush()
    for product_id, quantity in ordered_quantities.items():
        apply_inventory_movement(
            session,
            products[product_id],
            "sale",
            quantity,
            f"Order #{order.id}",
        )
    session.commit()
    session.refresh(order)
    return order


@router.post("/kitchen", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_kitchen_order(
    order_data: KitchenOrderCreate,
    session: Session = Depends(get_session),
) -> Order:
    subtotal = Decimal("0.00")
    products: dict[int, Product] = {}
    item_values = []
    for item in order_data.items:
        if item.productId is not None:
            product = session.get(Product, item.productId)
            if product is None:
                raise HTTPException(status_code=404, detail="Ordered product not found")
            products[item.productId] = product
        subtotal += Decimal(item.price) * item.quantity
        values = item.model_dump()
        values["price"] = float(item.price)
        item_values.append(values)

    if order_data.discount > subtotal:
        raise HTTPException(status_code=422, detail="Discount cannot exceed the subtotal")
    total = (
        (subtotal - order_data.discount) * (Decimal("1.00") + order_data.taxRate)
    ).quantize(Decimal("0.01"))
    order = Order(
        createdAt=order_data.createdAt or datetime.now(timezone.utc),
        status="awaiting_payment",
        kitchenStatus="queued",
        type=order_data.type,
        table=order_data.table,
        customer=order_data.customer,
        paymentMethod="Pending",
        discount=order_data.discount,
        taxRate=order_data.taxRate,
        total=total,
        items=item_values,
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    session: Session = Depends(get_session),
) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "refunded" and status_data.status == "paid":
        raise HTTPException(status_code=409, detail="A refunded order cannot be marked paid")
    if status_data.status == "refunded" and order.status != "paid":
        raise HTTPException(status_code=409, detail="Only paid orders can be refunded")

    if order.status == "paid" and status_data.status == "refunded":
        for item in order.items:
            product_id = item.get("productId")
            if product_id is None:
                continue
            product = session.get(Product, product_id)
            if product is not None:
                apply_inventory_movement(
                    session,
                    product,
                    "refund",
                    int(item["quantity"]),
                    f"Refund of order #{order.id}",
                )

    order.status = status_data.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{order_id}/payment", response_model=OrderRead)
def complete_kitchen_order_payment(
    order_id: int,
    payment_data: OrderPaymentCreate,
    session: Session = Depends(get_session),
) -> Order:
    order = session.exec(
        select(Order).where(Order.id == order_id).with_for_update()
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "awaiting_payment":
        raise HTTPException(status_code=409, detail="Order is not awaiting payment")
    if order.kitchenStatus != "ready":
        raise HTTPException(status_code=409, detail="Order can only be paid after the kitchen marks it ready")

    quantities: dict[int, int] = {}
    products: dict[int, Product] = {}
    stocks = {}
    for item in order.items:
        product_id = item.get("productId")
        if product_id is None:
            continue
        product = session.get(Product, product_id)
        if product is None:
            raise HTTPException(status_code=409, detail="An ordered product no longer exists")
        products[product_id] = product
        quantities[product_id] = quantities.get(product_id, 0) + int(item["quantity"])
        stocks[product_id] = get_or_create_stock(session, product_id)

    for product_id, quantity in quantities.items():
        if stocks[product_id].quantity < quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Not enough stock for {products[product_id].name} ({stocks[product_id].quantity} available)",
            )

    for product_id, quantity in quantities.items():
        apply_inventory_movement(
            session,
            products[product_id],
            "sale",
            quantity,
            f"Order #{order.id}",
        )
    order.status = "paid"
    order.paymentMethod = payment_data.paymentMethod
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{order_id}/kitchen-status", response_model=OrderRead)
def update_kitchen_status(
    order_id: int,
    status_data: KitchenStatusUpdate,
    session: Session = Depends(get_session),
) -> Order:
    order = session.exec(
        select(Order).where(Order.id == order_id).with_for_update()
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in KITCHEN_ORDER_STATUSES:
        raise HTTPException(status_code=409, detail="Only active orders can be prepared")
    if status_data.kitchenStatus == "completed" and order.status != "paid":
        raise HTTPException(status_code=409, detail="Order must be paid before it can be completed")
    expected_status = KITCHEN_TRANSITIONS.get(order.kitchenStatus)
    if status_data.kitchenStatus != expected_status:
        raise HTTPException(
            status_code=409,
            detail=f"Order must move from {order.kitchenStatus} to {expected_status or 'no further status'}",
        )

    order.kitchenStatus = status_data.kitchenStatus
    session.add(order)
    session.commit()
    session.refresh(order)
    return order