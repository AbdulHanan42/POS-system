from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models import RestaurantSettings
from app.schemas import RestaurantSettingsRead, RestaurantSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def get_or_create_settings(session: Session) -> RestaurantSettings:
    settings = session.get(RestaurantSettings, 1)
    if settings is None:
        settings = RestaurantSettings(id=1)
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