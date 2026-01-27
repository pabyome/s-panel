from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import asyncio
import logging
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
def get_system_stats(current_user: CurrentUser) -> Dict[str, Any]:
    return SystemMonitor.get_all_stats()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected")
    try:
        while True:
            stats = SystemMonitor.get_all_stats()
            await websocket.send_json(stats)
            await asyncio.sleep(1)  # Send updates every 1 second
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
