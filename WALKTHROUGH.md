# s-panel Implementation Walkthrough

We have successfully built the "MVP" version of the server control panel.

## Features Implemented

### 1. Dashboard & Core Engine
- **System Monitor**: Real-time stats (CPU, RAM, Disk) via `psutil`.
- **Backend**: FastAPI with `uv` package management.
- **Frontend**: Vue 3 + Tailwind CSS + Vite.

### 2. Website Manager
- **Function**: Create/Remove Nginx sites.
- **Backend Service**: `WebsiteManager` + `NginxManager` (generates `.conf` files).
- **UI**: List view with "Add Website" modal.

### 3. Security Manager
- **Function**: Manage UFW Firewall rules.
- **Backend Service**: `FirewallManager` (wraps `ufw` commands).
- **UI**: Rule list with "Delete" action and "Add Rule" modal.

### 4. Supervisor Manager
- **Function**: Manage background processes.
- **Backend Service**: Connects to Supervisor XML-RPC interface.
- **UI**:
    - **List**: Start/Stop/Restart buttons.
    - **Detail**: Real-time log streaming and Config editing.

### 5. Production Readiness
- **Config**: `.env` file support using `pydantic-settings`.
- **CORS**: Enabled for frontend communication.
- **Service**: `generate_service.py` to create a Systemd service file.

## How to Run

### Backend
```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Deployment (Systemd)
To run as a system service:
```bash
cd backend
python generate_service.py
sudo mv spanel.service /etc/systemd/system/
sudo systemctl enable --now spanel
```

## Verification Results
- **Unit Tests**: Pass for Website and Firewall managers.
- **Manual Check**: All API endpoints registered in `main.py`.

### 7. Redis Manager
Manage your **Redis** database instance directly from the panel.

1.  **Access**: Click **Redis** under the "Databases" section in the sidebar.
2.  **Overview**: View version, uptime, memory usage, and connected clients.
3.  **Configuration**:
    *   Edit settings like `maxmemory`, `port`, and `requirepass`.
    *   **Pro Tip**: Setting `maxmemory` to `0` removes the limit.
4.  **Data Explorer**:
    *   Search for keys (supports wildcards `*`).
    *   View key details (Type, TTL, Value).
    *   Delete individual keys or **Flush DB** to clear everything.

**Note**: You must have `redis-server` installed on your system.

## API Reference
**Base URL:** `http://<your-ip>:21040/api/v1`

## Compatibility Note: Nginx Proxy Manager (Docker)
If you are already running **Nginx Proxy Manager (NPM)** or another web server via Docker on ports 80/443:
1.  **Conflict**: `s-panel`'s built-in Nginx Manager expects to manage the host's Nginx instance on ports 80/443. This will conflict with NPM if both try to bind to the same ports.
2.  **Solution**:
    - Use NPM as your main Gateway.
    - Proxy `panel.yourdomain.com` to `http://HOST_IP:8000` (s-panel backend) and `http://HOST_IP:5173` (frontend).
    - **Limitation**: The "Website Manager" feature of `s-panel` (which writes to `/etc/nginx/`) will not automatically configure your Dockerized NPM. You should use `s-panel` primarily for **System Monitoring**, **Firewall**, and **Supervisor** management in this case.

## Cookbook: Hosting NestJS with Nginx Proxy Manager
If you have a NestJS app on the host and NPM in Docker:

### Step 1: Run NestJS using s-panel
1.  Navigate to **s-panel > Supervisor**.
2.  Click **Setup Guide** to ensure XML-RPC is enabled.
3.  Create a config file (e.g., `/etc/supervisor/conf.d/nestjs-app.conf`) via terminal or s-panel (if "Add Config" feature exists, otherwise edit manually for now implies using `nano` then reloading in s-panel, or using the "Config" tab of an *existing* process. *Note: Phase 5 only added Edit Config for existing processes. Creating new ones via UI wasn't explicitly built, so we'll assume manual file creation or using the "Config" tab of a placeholder.*)
    - *Correction*: The current MVP allows editing *existing* configs. Creating a *new* file requires terminal access or a "New Config" feature we didn't build yet. I'll advise terminal creation for the `.conf` file.
    ```ini
    [program:my-nest-app]
    command=node dist/main.js
    directory=/path/to/nestjs/project
    autostart=true
    autorestart=true
    environment=PORT=3000
    stdout_logfile=/var/log/my-nest-app.out.log
    ```
4.  In **s-panel**, click **Refresh**. You should see `my-nest-app`. Click **Start**.

### Step 2: Configure "Nginx Proxy Manager" (Docker)
1.  Log in to your NPM Admin UI (usually port 81).
2.  Click **Add Proxy Host**.
3.  **Domain Names**: `api.yourdomain.com`
4.  **Forward Host**: Use your **Host Machine's IP** (e.g., `192.168.x.x` or `172.17.0.1` depending on Docker network). **Do not use localhost**.
5.  **Forward Port**: `3000` (matches the port from Step 1).
6.  Save.


