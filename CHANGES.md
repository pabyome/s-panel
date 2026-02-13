# Changes

## Backend
- Modified `backend/app/services/docker_service.py`:
    - Added `_resolve_ip` helper method to resolve interface names to IPv4 addresses.
    - Updated `init_swarm` to use `_resolve_ip` for `advertise_addr`.
    - Added `list_images`, `list_networks`, and `list_volumes` methods.
- Modified `backend/app/schemas/docker.py`:
    - Added `ImageInfo`, `NetworkInfo`, and `VolumeInfo` schemas.
- Modified `backend/main.py`:
    - Registered `images`, `networks`, and `volumes` routers.
- Created `backend/app/api/v1/images.py`:
    - Added `GET /` endpoint to list images.
- Created `backend/app/api/v1/networks.py`:
    - Added `GET /` endpoint to list networks.
- Created `backend/app/api/v1/volumes.py`:
    - Added `GET /` endpoint to list volumes.

## Frontend
- Modified `frontend/src/router/index.js`:
    - Added routes for `/docker/images`, `/docker/networks`, `/docker/volumes`.
- Created `frontend/src/views/docker/Images.vue`:
    - View to list Docker images.
- Created `frontend/src/views/docker/Networks.vue`:
    - View to list Docker networks.
- Created `frontend/src/views/docker/Volumes.vue`:
    - View to list Docker volumes.

## System
- Modified `backend/app/services/system_monitor.py`:
    - Added `clear_system_memory` method to clear page cache, dentries, and inodes.
- Modified `backend/app/api/v1/system.py`:
    - Added `POST /memory/clear` endpoint.
- Modified `frontend/src/views/Monitor.vue`:
    - Added "Clear Cache" button and confirmation modal.
- Created `backend/tests/test_memory_clear.py`:
    - Tests for memory clearing logic and API.
