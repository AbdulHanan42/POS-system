from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.auth import require_roles
from app.inventory import apply_inventory_movement
from app.models import Product, Purchase
from app.schemas import PurchaseCreate, PurchaseItemRead, PurchaseRead

router = APIRouter(
    prefix="/purchases",
    tags=["purchases"],
    dependencies=[Depends(require_roles("Administrator", "Manager"))],
)


def purchase_read(purchase: Purchase) -> PurchaseRead:
    return PurchaseRead(
        id=purchase.id,
        supplier=purchase.supplier,
        status=purchase.status,
        createdAt=purchase.createdAt,
        total=float(purchase.total),
        items=[PurchaseItemRead(**item) for item in purchase.items],
    )


@router.get("", response_model=list[PurchaseRead])
def list_purchases(session: Session = Depends(get_session)) -> list[PurchaseRead]:
    purchases = session.exec(select(Purchase).order_by(Purchase.createdAt.desc())).all()
    return [purchase_read(purchase) for purchase in purchases]


@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(
    purchase_data: PurchaseCreate,
    session: Session = Depends(get_session),
) -> PurchaseRead:
    products: dict[int, Product] = {}
    items = []
    total = Decimal("0.00")
    for item in purchase_data.items:
        product = products.get(item.productId) or session.get(Product, item.productId)
        if product is None:
            raise HTTPException(status_code=404, detail="Purchased product not found")
        products[item.productId] = product
        unit_cost = item.unitCost.quantize(Decimal("0.01"))
        line_total = unit_cost * item.quantity
        total += line_total
        items.append({
            "productId": item.productId,
            "productName": product.name,
            "quantity": item.quantity,
            "unitCost": float(unit_cost),
            "lineTotal": float(line_total),
        })

    purchase = Purchase(
        supplier=purchase_data.supplier,
        status="pending",
        total=total,
        items=items,
    )
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return purchase_read(purchase)


@router.post("/{purchase_id}/receive", response_model=PurchaseRead)
def receive_purchase(
    purchase_id: int,
    session: Session = Depends(get_session),
) -> PurchaseRead:
    purchase = session.exec(
        select(Purchase).where(Purchase.id == purchase_id).with_for_update()
    ).first()
    if purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if purchase.status == "received":
        raise HTTPException(status_code=409, detail="Purchase has already been received")

    for item in purchase.items:
        product = session.get(Product, item["productId"])
        if product is None:
            raise HTTPException(status_code=409, detail="A purchased product no longer exists")
        apply_inventory_movement(
            session,
            product,
            "stock_in",
            item["quantity"],
            f"Purchase #{purchase.id} from {purchase.supplier}",
        )

    purchase.status = "received"
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return purchase_read(purchase)