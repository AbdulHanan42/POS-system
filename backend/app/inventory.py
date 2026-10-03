from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import InventoryMovement, InventoryStock, Product


def get_or_create_stock(session: Session, product_id: int) -> InventoryStock:
    stock = session.exec(
        select(InventoryStock)
        .where(InventoryStock.productId == product_id)
        .with_for_update()
    ).first()
    if stock is None:
        stock = InventoryStock(productId=product_id, quantity=0, reorderLevel=5)
        session.add(stock)
        session.flush()
    return stock


def apply_inventory_movement(
    session: Session,
    product: Product,
    movement_type: str,
    quantity: int,
    reason: str,
) -> InventoryStock:
    stock = get_or_create_stock(session, product.id)
    if movement_type in {"stock_out", "sale"}:
        if stock.quantity < quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Not enough stock for {product.name} ({stock.quantity} available)",
            )
        stock.quantity -= quantity
    else:
        stock.quantity += quantity

    stock.updatedAt = datetime.now(timezone.utc)
    session.add(stock)
    session.add(
        InventoryMovement(
            productId=product.id,
            movementType=movement_type,
            quantity=quantity,
            reason=reason,
        )
    )
    return stock