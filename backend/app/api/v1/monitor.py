import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket

from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()

@router.get("/stats")
def get_system_stats(current_user: CurrentUser) -> dict[str, Any]:
    return SystemMonitor.get_all_stats()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Use interval=None to calculate CPU usage since last call without blocking the event loop
            stats = SystemMonitor.get_all_stats(interval=None)
            await websocket.send_json(stats)
            await asyncio.sleep(1) # Send updates every 1 second
    except Exception:
        # Handle disconnection
        pass
