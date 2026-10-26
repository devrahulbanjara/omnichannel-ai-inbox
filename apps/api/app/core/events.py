"""Live updates: pushes small change notices to connected dashboards over WebSocket."""

from fastapi import WebSocket
from loguru import logger


class EventHub:
    """Connected dashboards in this API process. Without login, every dashboard gets every event."""

    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()

    def connect(self, websocket: WebSocket) -> None:
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    async def publish(self, event_type: str, **data: str) -> None:
        event = {"type": event_type, **data}
        for websocket in list(self.connections):
            try:
                await websocket.send_json(event)
            except Exception:
                logger.warning("Dropping a live connection that could not receive {}", event_type)
                self.disconnect(websocket)


events = EventHub()
