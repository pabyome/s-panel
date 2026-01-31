from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from typing import Dict, Any, List
import asyncio
import logging
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.broadcast_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        if len(self.active_connections) == 1:
            self.start_broadcast_loop()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if len(self.active_connections) == 0:
            self.stop_broadcast_loop()

    def start_broadcast_loop(self):
        if self.broadcast_task is None or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self.broadcast_loop())

    def stop_broadcast_loop(self):
        if self.broadcast_task:
            self.broadcast_task.cancel()
            self.broadcast_task = None

    async def broadcast_loop(self):
        try:
            while True:
                if not self.active_connections:
                    break
                try:
                    # Run blocking psutil calls in thread pool to avoid blocking event loop
                    stats = await asyncio.get_event_loop().run_in_executor(
                        None, SystemMonitor.get_all_stats
                    )
                    await self.broadcast(stats)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection likely closed
                pass


manager = ConnectionManager()


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
    await manager.connect(websocket)
    logger.info("WebSocket client connected")
    try:
        while True:
            # Keep connection open and wait for client disconnect
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except Exception:
                pass
