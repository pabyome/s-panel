from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from typing import Set, Dict, Any, List
import asyncio
import logging
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts system stats.
    Broadcasts stats to all connected clients via a single background task,
    preventing multiple expensive polling loops.
    """
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcast_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")

        # Start broadcast task if it's not running
        if not self.broadcast_task or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self.broadcast_loop())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast_loop(self):
        logger.info("Starting system monitor broadcast loop")
        try:
            while self.active_connections:
                # Run blocking psutil calls in thread pool
                stats = await asyncio.get_event_loop().run_in_executor(None, SystemMonitor.get_all_stats)

                # Broadcast to all connections
                # We collect dead connections to remove them safely
                to_remove = set()

                for connection in list(self.active_connections):
                    try:
                        if connection.client_state == WebSocketState.CONNECTED:
                            await connection.send_json(stats)
                    except Exception:
                        to_remove.add(connection)

                for conn in to_remove:
                    self.active_connections.discard(conn)

                # Wait for next update
                await asyncio.sleep(1)
        except Exception as e:
            logger.exception(f"Error in broadcast loop: {e}")
        finally:
            logger.info("Stopping system monitor broadcast loop")
            self.broadcast_task = None

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
    try:
        while True:
            # Keep connection alive and wait for disconnect
            # We don't expect messages from client
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Normal disconnect
        pass
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
