from fastapi import APIRouter, Depends, WebSocket
from typing import Dict, Any
import asyncio
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()

@router.get("/stats")
def get_system_stats(current_user: CurrentUser) -> Dict[str, Any]:
    return SystemMonitor.get_all_stats()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            stats = SystemMonitor.get_all_stats()
            await websocket.send_json(stats)
            await asyncio.sleep(1) # Send updates every 1 second
    except Exception:
        # Handle disconnection
        pass
