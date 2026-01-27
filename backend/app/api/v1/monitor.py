from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from typing import Dict, Any, List
import asyncio
import logging
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
def get_system_stats(current_user: CurrentUser) -> Dict[str, Any]:
    return SystemMonitor.get_all_stats()


@router.get("/processes", response_model=List[Dict[str, Any]])
def get_top_processes(
    current_user: CurrentUser,
    limit: int = 20
):
    return SystemMonitor.get_top_processes(limit)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected")
    try:
        while True:
            # Run blocking psutil calls in thread pool to avoid blocking event loop
            stats = await asyncio.get_event_loop().run_in_executor(None, SystemMonitor.get_all_stats)
            await websocket.send_json(stats)
            await asyncio.sleep(1)  # Send updates every 1 second
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except Exception:
                pass
