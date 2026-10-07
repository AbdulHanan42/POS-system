from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect


class OrderEventHub:
    def __init__(self) -> None:
        self.pos_clients: dict[int, set[WebSocket]] = defaultdict(set)
        self.customer_clients: dict[tuple[int, int], set[WebSocket]] = defaultdict(set)

    async def connect_pos(self, tenant_id: int, websocket: WebSocket) -> None:
        self.pos_clients[tenant_id].add(websocket)

    async def connect_customer(self, tenant_id: int, order_id: int, websocket: WebSocket) -> None:
        self.customer_clients[(tenant_id, order_id)].add(websocket)

    def disconnect_pos(self, tenant_id: int, websocket: WebSocket) -> None:
        self.pos_clients[tenant_id].discard(websocket)

    def disconnect_customer(self, tenant_id: int, order_id: int, websocket: WebSocket) -> None:
        self.customer_clients[(tenant_id, order_id)].discard(websocket)

    async def order_created(self, tenant_id: int, order_id: int, source: str) -> None:
        if source == "website":
            await self._broadcast(self.pos_clients[tenant_id], {
                "type": "order.created",
                "orderId": order_id,
                "source": source,
            })

    async def order_updated(self, tenant_id: int, order_id: int, status: str, kitchen_status: str, delivery_status: str) -> None:
        event = {
            "type": "order.updated",
            "orderId": order_id,
            "status": status,
            "kitchenStatus": kitchen_status,
            "deliveryStatus": delivery_status,
        }
        await self._broadcast(self.pos_clients[tenant_id], event)
        await self._broadcast(self.customer_clients[(tenant_id, order_id)], event)

    async def _broadcast(self, clients: set[WebSocket], event: dict) -> None:
        disconnected = []
        for websocket in tuple(clients):
            try:
                await websocket.send_json(event)
            except (WebSocketDisconnect, RuntimeError):
                disconnected.append(websocket)
        for websocket in disconnected:
            clients.discard(websocket)


order_events = OrderEventHub()