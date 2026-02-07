# Docker Management Feature

## Backend
- Modified `backend/pyproject.toml`: Added `psutil` dependency.
- Created `backend/app/api/v1/swarm.py`: Implemented Swarm API endpoints (Init, Leave, Nodes, Services, Stats).
- Modified `backend/app/services/docker_service.py`: Added Swarm management methods and system stats retrieval.
- Modified `backend/main.py`: Registered `swarm` router.
- Created `backend/tests/test_swarm.py`: Added backend tests for Swarm functionality.

## Frontend
- Created `frontend/src/views/DockerLayout.vue`: Implemented tabbed navigation layout.
- Created `frontend/src/views/docker/Overview.vue`: Implemented Overview dashboard with stats and container grid.
- Created `frontend/src/views/docker/Swarm.vue`: Implemented Swarm management view.
- Moved `frontend/src/views/Containers.vue` to `frontend/src/views/docker/Containers.vue`.
- Modified `frontend/src/router/index.js`: Updated routing for `/docker` and its children.
- Modified `frontend/src/components/Sidebar.vue`: Updated navigation link to Docker Overview.
- Created `frontend/tests/swarm.spec.js`: Added frontend tests for Swarm layout and navigation.
