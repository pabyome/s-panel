from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from typing import Dict, Any, List, Optional
import asyncio
import logging
from app.api.deps import CurrentUser
from app.services.system_monitor import SystemMonitor

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total clients: {len(self.active_connections)}")
        if len(self.active_connections) == 1 and not self.broadcast_task:
            self.start_broadcasting()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.active_connections)}")

        if len(self.active_connections) == 0 and self.broadcast_task:
            self.stop_broadcasting()

    def start_broadcasting(self):
        logger.info("Starting broadcast loop")
        self.broadcast_task = asyncio.create_task(self.broadcast_loop())

    def stop_broadcasting(self):
        if self.broadcast_task:
            logger.info("Stopping broadcast loop")
            self.broadcast_task.cancel()
            self.broadcast_task = None

    async def broadcast_loop(self):
        try:
            loop = asyncio.get_running_loop()
            while True:
                # Run blocking psutil calls in thread pool to avoid blocking event loop
                stats = await loop.run_in_executor(None, SystemMonitor.get_all_stats)

                # Broadcast to all
                # Copy list to avoid modification during iteration if disconnect happens inside loop (though disconnect is sync/async)
                # Actually iterating over list and awaiting send_json is fine as long as disconnect doesn't modify it concurrently.
                # Since asyncio is cooperative, modifications happen in other tasks.
                # But to be safe, we iterate a copy.
                for connection in list(self.active_connections):
                    try:
                        await connection.send_json(stats)
                    except Exception as e:
                        logger.error(f"Error sending to client: {e}")
                        # Force disconnect if send fails
                        self.disconnect(connection)

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Broadcast loop cancelled")
        except Exception as e:
            logger.error(f"Broadcast loop error: {e}")
            # Restart? For now just log.

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
            # Keep the connection open and wait for disconnect
            # We use receive_text() to wait for messages or disconnect
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
        manager.disconnect(websocket)
