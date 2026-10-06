from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth import require_roles
from app.database import get_session
from app.models import RestaurantSettings
from app.schemas import RestaurantSettingsRead, RestaurantSettingsUpdate

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    dependencies=[Depends(require_roles("Administrator", "Manager"))],
)


def get_or_create_settings(session: Session) -> RestaurantSettings:
    tenant_id = session.info["tenant_id"]
    settings = session.exec(
        select(RestaurantSettings).where(RestaurantSettings.tenantId == tenant_id)
    ).first()
    if settings is None:
        settings = RestaurantSettings(id=tenant_id, tenantId=tenant_id)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


@router.get("", response_model=RestaurantSettingsRead)
def read_settings(session: Session = Depends(get_session)) -> RestaurantSettings:
    return get_or_create_settings(session)


@router.put("", response_model=RestaurantSettingsRead)
def update_settings(
    settings_data: RestaurantSettingsUpdate,
    session: Session = Depends(get_session),
) -> RestaurantSettings:
    settings = get_or_create_settings(session)
    for field, value in settings_data.model_dump().items():
        setattr(settings, field, value)
    settings.updatedAt = datetime.now(timezone.utc)
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings