from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.auth import require_permission, require_roles
from app.inventory import apply_inventory_movement, get_or_create_stock
from app.models import InventoryMovement, InventoryStock, Product
from app.schemas import (
    InventoryAdjustmentCreate,
    InventoryMovementRead,
    InventoryStockRead,
    ReorderLevelUpdate,
)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(require_permission("inventory:read"))],
)


def inventory_item(product: Product, stock: InventoryStock) -> InventoryStockRead:
    if stock.quantity == 0:
        stock_status = "out_of_stock"
    elif stock.quantity <= stock.reorderLevel:
        stock_status = "low_stock"
    else:
        stock_status = "in_stock"
    unit_price = float(product.price)
    return InventoryStockRead(
        productId=product.id,
        name=product.name,
        category=product.category,
        image=product.image,
        unitPrice=unit_price,
        quantity=stock.quantity,
        reorderLevel=stock.reorderLevel,
        updatedAt=stock.updatedAt,
        stockValue=unit_price * stock.quantity,
        status=stock_status,
    )


@router.get("", response_model=list[InventoryStockRead])
def list_inventory(session: Session = Depends(get_session)) -> list[InventoryStockRead]:
    products = session.exec(select(Product).order_by(Product.name)).all()
    stock_rows = session.exec(select(InventoryStock)).all()
    stocks = {stock.productId: stock for stock in stock_rows}
    changed = False
    result = []
    for product in products:
        stock = stocks.get(product.id)
        if stock is None:
            stock = get_or_create_stock(session, product.id)
            changed = True
        result.append(inventory_item(product, stock))
    if changed:
        session.commit()
    return result


@router.get("/movements", response_model=list[InventoryMovementRead])
def list_movements(
    product_id: int | None = Query(default=None, alias="productId", gt=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[InventoryMovementRead]:
    statement = select(InventoryMovement).order_by(InventoryMovement.createdAt.desc())
    if product_id is not None:
        statement = statement.where(InventoryMovement.productId == product_id)
    movements = session.exec(statement.limit(limit)).all()
    product_ids = {movement.productId for movement in movements}
    products = {
        product.id: product
        for product in session.exec(select(Product).where(Product.id.in_(product_ids))).all()
    } if product_ids else {}
    return [
        InventoryMovementRead(
            id=movement.id,
            productId=movement.productId,
            productName=products[movement.productId].name
            if movement.productId in products
            else f"Deleted product #{movement.productId}",
            movementType=movement.movementType,
            quantity=movement.quantity,
            reason=movement.reason,
            createdAt=movement.createdAt,
        )
        for movement in movements
    ]


@router.post("/adjustments", response_model=InventoryStockRead)
def adjust_inventory(
    adjustment: InventoryAdjustmentCreate,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> InventoryStockRead:
    product = session.get(Product, adjustment.productId)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    stock = apply_inventory_movement(
        session,
        product,
        adjustment.movementType,
        adjustment.quantity,
        adjustment.reason,
    )
    session.commit()
    session.refresh(stock)
    return inventory_item(product, stock)


@router.patch("/products/{product_id}/reorder-level", response_model=InventoryStockRead)
def update_reorder_level(
    product_id: int,
    update: ReorderLevelUpdate,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> InventoryStockRead:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    stock = get_or_create_stock(session, product_id)
    stock.reorderLevel = update.reorderLevel
    stock.updatedAt = datetime.now(timezone.utc)
    session.add(stock)
    session.commit()
    session.refresh(stock)
    return inventory_item(product, stock)