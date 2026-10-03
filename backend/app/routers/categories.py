from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models import Category, Product
from app.schemas import CategoryCreate, CategoryDeleteResponse, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


def category_read(category: Category, product_count: int = 0) -> CategoryRead:
    return CategoryRead(
        id=category.id,
        name=category.name,
        description=category.description,
        isPizza=category.isPizza,
        productCount=product_count,
    )


def ensure_unique_name(name: str, session: Session, category_id: int | None = None) -> None:
    statement = select(Category).where(func.lower(Category.name) == name.lower())
    if category_id is not None:
        statement = statement.where(Category.id != category_id)
    if session.exec(statement).first() is not None:
        raise HTTPException(status_code=409, detail="A category with this name already exists")


@router.get("", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)) -> list[CategoryRead]:
    categories = session.exec(select(Category).order_by(Category.name)).all()
    product_counts = dict(
        session.exec(
            select(Product.category, func.count(Product.id)).group_by(Product.category)
        ).all()
    )
    return [
        category_read(category, product_counts.get(category.name, 0))
        for category in categories
    ]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
) -> CategoryRead:
    ensure_unique_name(category_data.name, session)
    category = Category(**category_data.model_dump())
    session.add(category)
    session.commit()
    session.refresh(category)
    return category_read(category)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
) -> CategoryRead:
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    ensure_unique_name(category_data.name, session, category_id)
    old_name = category.name
    for field, value in category_data.model_dump().items():
        setattr(category, field, value)
    if old_name != category.name:
        products = session.exec(select(Product).where(Product.category == old_name)).all()
        for product in products:
            product.category = category.name
            session.add(product)

    session.add(category)
    session.commit()
    session.refresh(category)
    product_count = session.exec(
        select(func.count(Product.id)).where(Product.category == category.name)
    ).one()
    return category_read(category, product_count)


@router.delete("/{category_id}", response_model=CategoryDeleteResponse)
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
) -> CategoryDeleteResponse:
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    product_count = session.exec(
        select(func.count(Product.id)).where(Product.category == category.name)
    ).one()
    if product_count:
        raise HTTPException(
            status_code=409,
            detail=f"Move or delete the {product_count} product(s) in this category first",
        )

    session.delete(category)
    session.commit()
    return CategoryDeleteResponse(message="Category deleted")