import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket
from sqlmodel import Session, select

from app.auth import has_permission
from app.database import engine
from app.event_hub import order_events
from app.models import AuthSession, Order, Tenant, UserAccount

router = APIRouter(tags=["order events"])


def offered_protocols(websocket: WebSocket) -> list[str]:
    return [value.strip() for value in websocket.headers.get("sec-websocket-protocol", "").split(",") if value.strip()]


@router.websocket("/ws/pos/orders")
async def pos_order_events(websocket: WebSocket) -> None:
    auth_protocol = next((value for value in offered_protocols(websocket) if value.startswith("pos-token.")), None)
    if auth_protocol is None:
        await websocket.close(code=4401)
        return

    token = auth_protocol.removeprefix("pos-token.")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with Session(engine) as session:
        auth_session = session.exec(select(AuthSession).where(
            AuthSession.tokenHash == token_hash,
            AuthSession.revokedAt.is_(None),
            AuthSession.expiresAt > datetime.now(timezone.utc),
        )).first()
        user = session.get(UserAccount, auth_session.userId) if auth_session else None
        if user is None or user.status != "active" or not has_permission(user, "orders:read"):
            await websocket.close(code=4403)
            return
        tenant_id = user.tenantId

    await websocket.accept(subprotocol="pos-orders")
    await order_events.connect_pos(tenant_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        order_events.disconnect_pos(tenant_id, websocket)


@router.websocket("/ws/public/orders/{order_id}")
async def customer_order_events(websocket: WebSocket, order_id: int, tenant: str = "legacy-workspace") -> None:
    protocols = offered_protocols(websocket)
    tracking_protocol = next((value for value in protocols if value.startswith("order-token.")), None)
    if tracking_protocol is None:
        await websocket.close(code=4401)
        return

    token = tracking_protocol.removeprefix("order-token.")
    with Session(engine) as session:
        workspace = session.exec(select(Tenant).where(Tenant.slug == tenant)).first()
        if workspace is None:
            await websocket.close(code=4404)
            return
        session.info["tenant_id"] = workspace.id
        order = session.exec(select(Order).where(Order.id == order_id)).first()
        if order is None or order.publicTrackingToken is None or not secrets.compare_digest(order.publicTrackingToken, token):
            await websocket.close(code=4404)
            return
        tenant_id = workspace.id

    await websocket.accept(subprotocol="order-tracking")
    await order_events.connect_customer(tenant_id, order_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        order_events.disconnect_customer(tenant_id, order_id, websocket)