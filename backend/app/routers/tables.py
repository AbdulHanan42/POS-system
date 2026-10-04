from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.auth import require_permission, require_roles
from app.models import RestaurantTable
from app.schemas import RestaurantTableCreate, RestaurantTableRead, TableDeleteResponse

router = APIRouter(
    prefix="/tables",
    tags=["tables"],
    dependencies=[Depends(require_permission("tables:read"))],
)


@router.get("", response_model=list[RestaurantTableRead])
def list_tables(session: Session = Depends(get_session)) -> list[RestaurantTable]:
    return list(session.exec(select(RestaurantTable).order_by(RestaurantTable.id)).all())


@router.post("", response_model=RestaurantTableRead, status_code=status.HTTP_201_CREATED)
def create_table(
    table_data: RestaurantTableCreate,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> RestaurantTable:
    table = RestaurantTable(**table_data.model_dump())
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@router.put("/{table_id}", response_model=RestaurantTableRead)
def update_table(
    table_id: int,
    table_data: RestaurantTableCreate,
    user=Depends(require_permission("tables:update")),
    session: Session = Depends(get_session),
) -> RestaurantTable:
    table = session.get(RestaurantTable, table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    if user.role == "Waiter" and (table_data.name != table.name or table_data.seats != table.seats):
        raise HTTPException(status_code=403, detail="Waiters can only change table status")

    for field, value in table_data.model_dump().items():
        setattr(table, field, value)
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@router.delete("/{table_id}", response_model=TableDeleteResponse)
def delete_table(
    table_id: int,
    user=Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> TableDeleteResponse:
    table = session.get(RestaurantTable, table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    session.delete(table)
    session.commit()
    return TableDeleteResponse(message="Table deleted")