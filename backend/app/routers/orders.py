from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Order
from app.schemas import OrderCreate, OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


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

    order.status = status_data.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order