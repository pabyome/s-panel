# Changes

## New Feature: File Manager

Added a fully functional File Manager to the backend and frontend.

### Backend

- **Created `backend/app/services/file_manager.py`**:
  - Implements `FileManager` service class.
  - Features: List directory, Read file, Create directory, Save file, Delete item.
  - Includes basic security checks (path validation, size limit for reading).

- **Created `backend/app/api/v1/files.py`**:
  - Defines API endpoints for file operations:
    - `GET /list`: List files in a directory.
    - `GET /content`: Read file content.
    - `POST /folder`: Create a new folder.
    - `POST /content`: Save file content.
    - `DELETE /`: Delete a file or directory.

- **Updated `backend/main.py`**:
  - Registered the new `files` router.

### Frontend

- **Created `frontend/src/views/FileManager.vue`**:
  - Vue component for the File Manager UI.
  - Features:
    - Breadcrumb navigation.
    - File listing with sorting and details (size, permissions, owner).
    - File editing modal.
    - Create folder modal.
    - Delete confirmation.

- **Updated `frontend/src/router/index.js`**:
  - Added route `/files` pointing to `FileManager.vue`.

- **Updated `frontend/src/components/Sidebar.vue`**:
  - Added "File Manager" link to the navigation sidebar.
