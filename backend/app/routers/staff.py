from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.auth import require_roles
from app.models import StaffMember
from app.schemas import StaffCreate, StaffRead

router = APIRouter(
    prefix="/staff",
    tags=["staff"],
    dependencies=[Depends(require_roles("Administrator", "Manager"))],
)


@router.get("", response_model=list[StaffRead])
def list_staff(session: Session = Depends(get_session)) -> list[StaffMember]:
    return list(session.exec(select(StaffMember).order_by(StaffMember.name)).all())


@router.post("", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: StaffCreate,
    session: Session = Depends(get_session),
) -> StaffMember:
    existing = session.exec(
        select(StaffMember).where(StaffMember.email == staff_data.email)
    ).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="A staff member with this email already exists")

    staff_member = StaffMember(**staff_data.model_dump())
    session.add(staff_member)
    session.commit()
    session.refresh(staff_member)
    return staff_member


@router.put("/{staff_id}", response_model=StaffRead)
def update_staff(
    staff_id: int,
    staff_data: StaffCreate,
    session: Session = Depends(get_session),
) -> StaffMember:
    staff_member = session.get(StaffMember, staff_id)
    if staff_member is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    duplicate = session.exec(
        select(StaffMember).where(
            StaffMember.email == staff_data.email,
            StaffMember.id != staff_id,
        )
    ).first()
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="A staff member with this email already exists")

    for field, value in staff_data.model_dump().items():
        setattr(staff_member, field, value)
    session.add(staff_member)
    session.commit()
    session.refresh(staff_member)
    return staff_member


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, session: Session = Depends(get_session)) -> None:
    staff_member = session.get(StaffMember, staff_id)
    if staff_member is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    session.delete(staff_member)
    session.commit()