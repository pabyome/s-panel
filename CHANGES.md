# Changes

## Backend
- **Created** `backend/app/services/file_manager.py`: Implemented `FileManager` service for file system operations.
- **Created** `backend/app/api/v1/files.py`: Added API endpoints for file management.
- **Modified** `backend/main.py`: Registered the new `files` router.
- **Created** `backend/tests/test_files.py`: Added unit tests for the file manager API.

## Frontend
- **Created** `frontend/src/views/FileManager.vue`: Added the file manager interface (list, edit, delete, create).
- **Modified** `frontend/src/router/index.js`: Added the `/files` route.
- **Modified** `frontend/src/components/Sidebar.vue`: Added "Files" to the sidebar navigation.
