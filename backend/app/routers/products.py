from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.auth import require_permission, require_roles
from app.models import InventoryStock, Product
from app.schemas import ProductCreate, ProductDeleteResponse, ProductRead

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(require_permission("catalog:read"))],
)


@router.get("", response_model=list[ProductRead])
def list_products(session: Session = Depends(get_session)) -> list[Product]:
    return list(session.exec(select(Product).order_by(Product.id)).all())


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> Product:
    product_values = product_data.model_dump(exclude={"prices"})
    product_values["prices"] = (
        product_data.prices.model_dump() if product_data.prices else None
    )
    product = Product(**product_values)
    session.add(product)
    session.flush()
    session.add(InventoryStock(productId=product.id, quantity=0, reorderLevel=5))
    session.commit()
    session.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_values = product_data.model_dump(exclude={"prices"})
    product_values["prices"] = (
        product_data.prices.model_dump() if product_data.prices else None
    )
    for field, value in product_values.items():
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
def delete_product(
    product_id: int,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> ProductDeleteResponse:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    stock = session.exec(
        select(InventoryStock).where(InventoryStock.productId == product_id)
    ).first()
    if stock is not None:
        session.delete(stock)
    session.delete(product)
    session.commit()
    return ProductDeleteResponse(message="Product deleted")