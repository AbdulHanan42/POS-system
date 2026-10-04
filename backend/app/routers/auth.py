import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.auth import (
    create_session,
    bearer_scheme,
    get_current_user,
    hash_password,
    require_roles,
    user_response,
    verify_password,
)
from app.database import get_session
from app.models import AuthSession, RestaurantSettings, Tenant, UserAccount
from app.schemas import (
    AuthLogin,
    AuthSessionRead,
    AuthSignup,
    AuthUserCreate,
    AuthUserListRead,
    AuthUserRead,
    AuthUserStatusUpdate,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def slug_for_tenant(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-") or "restaurant"
    return f"{slug[:80]}-{secrets.token_hex(4)}"


def build_session_response(session: Session, user: UserAccount) -> AuthSessionRead:
    tenant = session.get(Tenant, user.tenantId)
    token, expires_at = create_session(session, user)
    session.commit()
    return AuthSessionRead(
        accessToken=token,
        expiresAt=expires_at,
        user=user_response(user, tenant),
    )


@router.post("/signup", response_model=AuthSessionRead, status_code=status.HTTP_201_CREATED)
def signup(
    signup_data: AuthSignup,
    session: Session = Depends(get_session),
) -> AuthSessionRead:
    if session.exec(select(UserAccount).where(UserAccount.email == signup_data.email)).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    legacy_tenant = session.exec(
        select(Tenant).where(Tenant.slug == "legacy-workspace").with_for_update()
    ).first()
    first_account = session.exec(select(UserAccount.id).limit(1)).first() is None
    if first_account and legacy_tenant is not None:
        tenant = legacy_tenant
        tenant.name = signup_data.tenantName
        session.add(tenant)
    else:
        tenant = Tenant(name=signup_data.tenantName, slug=slug_for_tenant(signup_data.tenantName))
        session.add(tenant)
        session.flush()

    user = UserAccount(
        tenantId=tenant.id,
        name=signup_data.name,
        email=signup_data.email,
        passwordHash=hash_password(signup_data.password),
        role="Administrator",
        status="active",
    )
    session.add(user)
    session.flush()

    settings = session.exec(
        select(RestaurantSettings).where(RestaurantSettings.tenantId == tenant.id)
    ).first()
    if settings is None:
        settings = RestaurantSettings(
            id=tenant.id,
            tenantId=tenant.id,
            restaurantName=signup_data.tenantName,
            email=signup_data.email,
        )
        session.add(settings)
    else:
        settings.restaurantName = signup_data.tenantName
        settings.email = signup_data.email
        session.add(settings)

    return build_session_response(session, user)


@router.post("/login", response_model=AuthSessionRead)
def login(
    credentials: AuthLogin,
    session: Session = Depends(get_session),
) -> AuthSessionRead:
    user = session.exec(
        select(UserAccount).where(UserAccount.email == credentials.email)
    ).first()
    if user is None or user.status != "active" or not verify_password(credentials.password, user.passwordHash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return build_session_response(session, user)


@router.get("/me", response_model=AuthUserRead)
def current_account(
    user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AuthUserRead:
    tenant = session.get(Tenant, user.tenantId)
    return AuthUserRead(**user_response(user, tenant))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    user: UserAccount = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> None:
    import hashlib

    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    auth_session = session.exec(
        select(AuthSession).where(AuthSession.tokenHash == token_hash)
    ).first()
    if auth_session is not None:
        auth_session.revokedAt = datetime.now(timezone.utc)
        session.add(auth_session)
        session.commit()


@router.get("/users", response_model=list[AuthUserListRead])
def list_accounts(
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> list[UserAccount]:
    return list(
        session.exec(
            select(UserAccount)
            .where(UserAccount.tenantId == user.tenantId)
            .order_by(UserAccount.name)
        ).all()
    )


@router.post("/users", response_model=AuthUserListRead, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AuthUserCreate,
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> UserAccount:
    if session.exec(select(UserAccount).where(UserAccount.email == account_data.email)).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    account = UserAccount(
        tenantId=user.tenantId,
        name=account_data.name,
        email=account_data.email,
        passwordHash=hash_password(account_data.password),
        role=account_data.role,
        status="active",
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.patch("/users/{user_id}/status", response_model=AuthUserListRead)
def update_account_status(
    user_id: int,
    update: AuthUserStatusUpdate,
    user: UserAccount = Depends(require_roles("Administrator", "Manager")),
    session: Session = Depends(get_session),
) -> UserAccount:
    account = session.exec(
        select(UserAccount).where(
            UserAccount.id == user_id,
            UserAccount.tenantId == user.tenantId,
        )
    ).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.id == user.id and update.status == "inactive":
        raise HTTPException(status_code=409, detail="You cannot deactivate your own account")
    if account.role == "Administrator" and update.status == "inactive":
        active_admins = session.exec(
            select(UserAccount.id).where(
                UserAccount.tenantId == user.tenantId,
                UserAccount.role == "Administrator",
                UserAccount.status == "active",
            )
        ).all()
        if len(active_admins) <= 1:
            raise HTTPException(status_code=409, detail="The last active administrator cannot be deactivated")

    account.status = update.status
    session.add(account)
    session.commit()
    session.refresh(account)
    return account