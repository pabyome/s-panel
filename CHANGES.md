
# Changes - Nginx WAF Feature

## New Features
- **WAF (Web Application Firewall)**: Implemented Nginx-based WAF for websites.
    - **CC Defense**: Rate limiting (requests/second) and burst handling.
    - **Keyword Blocking**: Block requests based on URI keywords.
    - **Scanner Blocking**: Block common vulnerability scanners (User-Agent).
    - **Hacker Blocking**: Block common SQL injection and XSS patterns in query strings.
- **SSL Support**: Updated Nginx configuration generation to support SSL/HTTPS (redirect HTTP to HTTPS).
- **Frontend UI**: Added WAF management tab in the Website Management modal.

## Modified Files
- `backend/app/services/nginx_manager.py`: Updated to support WAF configuration generation and SSL handling.
- `backend/app/schemas/waf.py`: Created Pydantic schemas for WAF configuration.
- `backend/app/models/waf.py`: Created SQLModel for WAF configuration.
- `backend/app/api/v1/waf.py`: Created API endpoints for WAF management.
- `backend/main.py`: Registered `waf` router.
- `backend/tests/test_waf.py`: Created tests for WAF functionality.
- `frontend/src/components/ManageWebsiteModal.vue`: Added WAF configuration UI.

## API Endpoints
- `GET /api/v1/waf/{website_id}`: Get WAF configuration.
- `POST /api/v1/waf/{website_id}`: Update WAF configuration.

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

