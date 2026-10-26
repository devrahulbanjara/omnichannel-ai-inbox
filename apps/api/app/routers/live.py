from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import events

router = APIRouter(tags=["live"])


@router.websocket("/live")
async def live_updates(websocket: WebSocket) -> None:
    """Sends {"type", "conversation_id"} whenever a conversation changes."""
    await websocket.accept()
    events.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # the dashboard sends nothing; this waits for close
    except WebSocketDisconnect:
        events.disconnect(websocket)
