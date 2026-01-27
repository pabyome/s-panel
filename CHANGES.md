# Changes

## Backend
- Created `backend/app/services/file_manager.py`: Implemented `FileManager` service for file system operations.
- Created `backend/app/api/v1/files.py`: Implemented API endpoints for file management.
- Modified `backend/main.py`: Registered `files` router.

## Frontend
- Created `frontend/src/views/FileManager.vue`: Implemented File Manager UI.
- Modified `frontend/src/router/index.js`: Added `/files` route.
- Modified `frontend/src/components/Sidebar.vue`: Added "File Manager" link to sidebar.

## Tests
- Created `backend/tests/test_files.py`: Added tests for file management API.
