from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_roles
from app.database import get_session
from app.models import DeliveryZone, Order, UserAccount
from app.schemas import (
    DeliveryZoneCreate,
    DeliveryZoneRead,
    DeliveryZoneUpdate,
    DeliveryStatusUpdate,
)

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.get("/zones", response_model=list[DeliveryZoneRead])
def list_delivery_zones(
    user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[DeliveryZone]:
    return list(
        session.exec(
            select(DeliveryZone)
            .where(DeliveryZone.tenantId == user.tenantId)
            .order_by(DeliveryZone.name)
        ).all()
    )


@router.post("/zones", response_model=DeliveryZoneRead, status_code=status.HTTP_201_CREATED)
def create_delivery_zone(
    zone_data: DeliveryZoneCreate,
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> DeliveryZone:
    existing = session.exec(
        select(DeliveryZone).where(
            DeliveryZone.tenantId == user.tenantId,
            DeliveryZone.name == zone_data.name,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Delivery zone with this name already exists")

    zone = DeliveryZone(
        tenantId=user.tenantId,
        name=zone_data.name,
        description=zone_data.description,
        fee=zone_data.fee,
        minOrderAmount=zone_data.minOrderAmount,
        estimatedTime=zone_data.estimatedTime,
        status=zone_data.status,
    )
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


@router.get("/zones/{zone_id}", response_model=DeliveryZoneRead)
def get_delivery_zone(
    zone_id: int,
    user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DeliveryZone:
    zone = session.exec(
        select(DeliveryZone).where(
            DeliveryZone.id == zone_id,
            DeliveryZone.tenantId == user.tenantId,
        )
    ).first()
    if zone is None:
        raise HTTPException(status_code=404, detail="Delivery zone not found")
    return zone


@router.patch("/zones/{zone_id}", response_model=DeliveryZoneRead)
def update_delivery_zone(
    zone_id: int,
    update: DeliveryZoneUpdate,
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> DeliveryZone:
    zone = session.exec(
        select(DeliveryZone).where(
            DeliveryZone.id == zone_id,
            DeliveryZone.tenantId == user.tenantId,
        )
    ).first()
    if zone is None:
        raise HTTPException(status_code=404, detail="Delivery zone not found")

    if update.name is not None:
        zone.name = update.name
    if update.description is not None:
        zone.description = update.description
    if update.fee is not None:
        zone.fee = update.fee
    if update.minOrderAmount is not None:
        zone.minOrderAmount = update.minOrderAmount
    if update.estimatedTime is not None:
        zone.estimatedTime = update.estimatedTime
    if update.status is not None:
        zone.status = update.status

    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery_zone(
    zone_id: int,
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> None:
    zone = session.exec(
        select(DeliveryZone).where(
            DeliveryZone.id == zone_id,
            DeliveryZone.tenantId == user.tenantId,
        )
    ).first()
    if zone is None:
        raise HTTPException(status_code=404, detail="Delivery zone not found")

    session.delete(zone)
    session.commit()


@router.get("/orders")
def list_delivery_orders(
    user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Order]:
    return list(
        session.exec(
            select(Order)
            .where(
                Order.tenantId == user.tenantId,
                Order.type == "Delivery",
                Order.deliveryStatus != "cancelled",
            )
            .order_by(Order.createdAt.desc())
        ).all()
    )


@router.patch("/orders/{order_id}/status")
def update_delivery_status(
    order_id: int,
    update: DeliveryStatusUpdate,
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> Order:
    order = session.exec(
        select(Order).where(
            Order.id == order_id,
            Order.tenantId == user.tenantId,
        )
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order.deliveryStatus = update.deliveryStatus

    if update.deliveryStatus == "delivered" and not update.actualDeliveryTime:
        order.actualDeliveryTime = datetime.now(timezone.utc)
    elif update.actualDeliveryTime:
        order.actualDeliveryTime = update.actualDeliveryTime

    if update.deliveryStatus == "pending":
        order.estimatedDeliveryTime = None
    elif update.deliveryStatus == "preparing":
        zone = session.exec(
            select(DeliveryZone).where(DeliveryZone.name == order.deliveryZone)
        ).first()
        if zone:
            order.estimatedDeliveryTime = datetime.now(timezone.utc) + timedelta(minutes=zone.estimatedTime)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order
