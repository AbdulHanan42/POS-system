from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models import ModifierGroup, Product
from app.schemas import ModifierDeleteResponse, ModifierGroupCreate, ModifierGroupRead

router = APIRouter(prefix="/modifiers", tags=["modifiers"])


def ensure_unique_name(name: str, session: Session, group_id: int | None = None) -> None:
    statement = select(ModifierGroup).where(func.lower(ModifierGroup.name) == name.lower())
    if group_id is not None:
        statement = statement.where(ModifierGroup.id != group_id)
    if session.exec(statement).first() is not None:
        raise HTTPException(status_code=409, detail="A modifier group with this name already exists")


def validate_product_ids(product_ids: list[int], session: Session) -> None:
    unique_ids = set(product_ids)
    if len(unique_ids) != len(product_ids):
        raise HTTPException(status_code=422, detail="Product assignments must not contain duplicates")
    if not unique_ids:
        return
    existing_ids = set(
        session.exec(select(Product.id).where(Product.id.in_(unique_ids))).all()
    )
    if existing_ids != unique_ids:
        raise HTTPException(status_code=422, detail="One or more assigned products do not exist")


def group_values(group_data: ModifierGroupCreate) -> dict:
    values = group_data.model_dump(exclude={"options"})
    values["options"] = [option.model_dump() for option in group_data.options]
    return values


@router.get("", response_model=list[ModifierGroupRead])
def list_modifier_groups(session: Session = Depends(get_session)) -> list[ModifierGroup]:
    return list(session.exec(select(ModifierGroup).order_by(ModifierGroup.name)).all())


@router.post("", response_model=ModifierGroupRead, status_code=status.HTTP_201_CREATED)
def create_modifier_group(
    group_data: ModifierGroupCreate,
    session: Session = Depends(get_session),
) -> ModifierGroup:
    ensure_unique_name(group_data.name, session)
    validate_product_ids(group_data.productIds, session)
    group = ModifierGroup(**group_values(group_data))
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


@router.put("/{group_id}", response_model=ModifierGroupRead)
def update_modifier_group(
    group_id: int,
    group_data: ModifierGroupCreate,
    session: Session = Depends(get_session),
) -> ModifierGroup:
    group = session.get(ModifierGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Modifier group not found")

    ensure_unique_name(group_data.name, session, group_id)
    validate_product_ids(group_data.productIds, session)
    for field, value in group_values(group_data).items():
        setattr(group, field, value)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


@router.delete("/{group_id}", response_model=ModifierDeleteResponse)
def delete_modifier_group(
    group_id: int,
    session: Session = Depends(get_session),
) -> ModifierDeleteResponse:
    group = session.get(ModifierGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Modifier group not found")
    session.delete(group)
    session.commit()
    return ModifierDeleteResponse(message="Modifier group deleted")