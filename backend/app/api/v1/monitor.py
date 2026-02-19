from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from starlette.websockets import WebSocketState
from typing import Dict, Any, List, Optional
import asyncio
import logging
import jwt
from pydantic import ValidationError
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor
from app.core.security import ALGORITHM, SECRET_KEY

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
        if len(self.active_connections) == 1:
            self.start_broadcast_task()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
        if len(self.active_connections) == 0:
            self.stop_broadcast_task()

    def start_broadcast_task(self):
        if self.broadcast_task is None or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self.broadcast_loop())
            logger.info("Started system monitor broadcast task")

    def stop_broadcast_task(self):
        if self.broadcast_task:
            self.broadcast_task.cancel()
            self.broadcast_task = None
            logger.info("Stopped system monitor broadcast task")

    async def broadcast_loop(self):
        try:
            while True:
                try:
                    # Optimized: Fetch stats once for all clients
                    # Use asyncio.to_thread for blocking psutil calls
                    stats = await asyncio.to_thread(SystemMonitor.get_all_stats)

                    # Broadcast to all
                    disconnected_ws = []
                    # Iterate over a copy of the list to handle modifications during iteration
                    for connection in list(self.active_connections):
                        try:
                            await connection.send_json(stats)
                        except Exception:
                            disconnected_ws.append(connection)

                    # Clean up disconnected
                    for ws in disconnected_ws:
                        self.disconnect(ws)
                except Exception as e:
                    logger.exception(f"Error in broadcast loop iteration: {e}")

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Critical error in broadcast loop: {e}")

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
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Authenticate via Token
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (jwt.PyJWTError, ValidationError):
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection open and listen for client messages (if any)
            # wait for disconnect
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        manager.disconnect(websocket)
