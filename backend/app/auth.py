import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.database import get_session
from app.models import AuthSession, Tenant, UserAccount

PASSWORD_ITERATIONS = 600_000
SESSION_HOURS = 12
ROLE_PERMISSIONS = {
    "Administrator": ["*"],
    "Manager": ["*"],
    "Cashier": [
        "pos:use",
        "catalog:read",
        "orders:read",
        "orders:create",
        "orders:payment",
        "inventory:read",
        "customers:manage",
    ],
    "Chef": ["kitchen:read", "kitchen:update", "orders:read"],
    "Waiter": [
        "pos:use",
        "catalog:read",
        "orders:read",
        "orders:create",
        "inventory:read",
        "tables:read",
        "tables:update",
        "customers:manage",
    ],
}

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return "$".join((
        "pbkdf2_sha256",
        str(PASSWORD_ITERATIONS),
        base64.urlsafe_b64encode(salt).decode().rstrip("="),
        base64.urlsafe_b64encode(derived).decode().rstrip("="),
    ))


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations, salt_text, hash_text = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text + "=" * (-len(salt_text) % 4))
        expected = base64.urlsafe_b64decode(hash_text + "=" * (-len(hash_text) % 4))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def permission_names(role: str) -> list[str]:
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user: UserAccount, permission: str) -> bool:
    permissions = permission_names(user.role)
    return "*" in permissions or permission in permissions


def require_permission(permission: str) -> Callable:
    def check_permission(user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if not has_permission(user, permission):
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
        return user

    return check_permission


def require_roles(*roles: str) -> Callable:
    def check_role(user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Your role cannot perform this action")
        return user

    return check_role


def create_session(session: Session, user: UserAccount) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session.add(AuthSession(userId=user.id, tokenHash=token_hash, expiresAt=expires_at))
    return token, expires_at


def user_response(user: UserAccount, tenant: Tenant) -> dict:
    return {
        "id": user.id,
        "tenantId": user.tenantId,
        "tenantName": tenant.name,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "permissions": permission_names(user.role),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> UserAccount:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    auth_session = session.exec(
        select(AuthSession).where(
            AuthSession.tokenHash == token_hash,
            AuthSession.revokedAt.is_(None),
            AuthSession.expiresAt > datetime.now(timezone.utc),
        )
    ).first()
    if auth_session is None:
        raise unauthorized

    user = session.get(UserAccount, auth_session.userId)
    if user is None or user.status != "active":
        raise unauthorized
    session.info["tenant_id"] = user.tenantId
    return user