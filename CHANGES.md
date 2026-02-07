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
