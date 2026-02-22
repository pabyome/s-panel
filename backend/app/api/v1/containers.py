from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from typing import List, Any
import asyncio
import jwt
import json
import logging
from app.api.deps import CurrentUser
from app.services.docker_service import docker_service
from app.schemas.docker import ContainerInfo, LogResponse, ContainerCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/run", response_model=ContainerInfo)
def run_container(
    container_in: ContainerCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Run a new container.
    """
    try:
        container = docker_service.run_container(container_in)
        return container
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ContainerInfo])
def list_containers(
    current_user: CurrentUser,
) -> Any:
    """
    List all containers.
    """
    try:
        containers = docker_service.list_containers()
        return containers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{container_id}", response_model=ContainerInfo)
def get_container(
    container_id: str,
    current_user: CurrentUser,
) -> Any:
    """
    Get container by ID.
    """
    try:
        container = docker_service.get_container(container_id)
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        return container
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{container_id}/{action}", response_model=Any)
def perform_action(
    container_id: str,
    action: str,
    current_user: CurrentUser,
) -> Any:
    """
    Perform action on container (start, stop, restart, pause, unpause, remove).
    """
    valid_actions = ["start", "stop", "restart", "pause", "unpause", "remove"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of {valid_actions}")

    try:
        container = docker_service.perform_action(container_id, action)

        if action == "remove":
             return {"message": "Container removed"}

        if not container:
             raise HTTPException(status_code=404, detail="Container not found")

        return container
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{container_id}/logs", response_model=LogResponse)
def get_logs(
    container_id: str,
    current_user: CurrentUser,
    tail: int = 200,
) -> Any:
    """
    Get container logs.
    """
    try:
        logs = docker_service.get_logs(container_id, tail=tail)
        return LogResponse(logs=logs)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/{container_id}/terminal")
async def terminal_websocket(
    websocket: WebSocket,
    container_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for interactive container terminal.
    """
    # Verify Token
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except (jwt.PyJWTError, Exception):
         await websocket.close(code=1008, reason="Invalid authentication token")
         return

    await websocket.accept()

    sock = None
    try:
        # Create exec instance
        # Try to use bash if available, otherwise fall back to sh.
        # This command checks for bash and execs it, or falls back to sh.
        # We wrap it in sh to ensure portability.
        cmd = ["/bin/sh", "-c", "if [ -x /bin/bash ]; then exec /bin/bash; else exec /bin/sh; fi"]
        exec_id = docker_service.exec_create(container_id, cmd)

        # Start exec and get socket
        sock = docker_service.exec_start(exec_id)

        # Helper to read from docker socket and send to websocket
        async def read_from_docker():
            try:
                while True:
                    data = await asyncio.to_thread(sock.recv, 4096)
                    if not data:
                        break
                    await websocket.send_text(data.decode('utf-8', errors='replace'))
            except Exception as e:
                # Expected when socket closed
                pass
            finally:
                # If docker closes, we close websocket
                try:
                    await websocket.close()
                except:
                    pass

        # Helper to read from websocket and write to docker socket
        async def write_to_docker():
            try:
                while True:
                    data = await websocket.receive_text()
                    # Check if it's a resize command (JSON)
                    try:
                        # Optimization: only try to parse if it looks like JSON
                        if data.strip().startswith('{'):
                             msg = json.loads(data)
                             if 'cols' in msg and 'rows' in msg:
                                 docker_service.exec_resize(exec_id, height=msg['rows'], width=msg['cols'])
                                 continue
                    except json.JSONDecodeError:
                        pass

                    # Otherwise write to socket
                    await asyncio.to_thread(sock.send, data.encode('utf-8'))
            except WebSocketDisconnect:
                pass
            except Exception as e:
                 logger.error(f"Error writing to docker: {e}")
            finally:
                 # If websocket closes, we assume session is done
                 try:
                    sock.close()
                 except:
                    pass

        # Run tasks
        await asyncio.gather(read_from_docker(), write_to_docker())

    except Exception as e:
        logger.error(f"Terminal error: {e}")
        try:
             await websocket.close(code=1011, reason=str(e))
        except:
             pass
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass
