import asyncio
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
def get_system_stats(current_user: CurrentUser) -> dict[str, Any]:
    return SystemMonitor.get_all_stats()


@router.get("/processes", response_model=list[dict[str, Any]])
def get_top_processes(
    current_user: CurrentUser,
    limit: int = 20
):
    return SystemMonitor.get_top_processes(limit)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.broadcast_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
        if len(self.active_connections) == 1 and (self.broadcast_task is None or self.broadcast_task.done()):
            self.broadcast_task = asyncio.create_task(self.start_broadcast())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

        if len(self.active_connections) == 0 and self.broadcast_task:
            self.broadcast_task.cancel()
            self.broadcast_task = None

    async def start_broadcast(self):
        try:
            while len(self.active_connections) > 0:
                stats = await asyncio.get_event_loop().run_in_executor(None, SystemMonitor.get_all_stats)
                await self.broadcast(stats)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Broadcast error: {e}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        manager.disconnect(websocket)
