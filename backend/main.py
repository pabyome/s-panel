from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from sqlmodel import Session
from app.models.database import create_db_and_tables, engine
from app.services.auth_service import AuthService
from app.api.v1 import auth, monitor, websites, firewall, supervisor, system, deployments, redis, cron, backups, logs
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run auto-migrations first to ensure schema is correct for models
    from app.core.migrations import run_migrations
    run_migrations()

    create_db_and_tables()
    with Session(engine) as session:
        auth_service = AuthService(session)
        auth_service.ensure_admin_exists()
    yield

app = FastAPI(title="s-panel", version="0.1.0", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["monitor"])
app.include_router(websites.router, prefix="/api/v1/websites", tags=["websites"])
app.include_router(firewall.router, prefix="/api/v1/firewall", tags=["firewall"])
app.include_router(supervisor.router, prefix="/api/v1/supervisor", tags=["supervisor"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["deployments"])
app.include_router(redis.router, prefix="/api/v1/redis", tags=["redis"])
app.include_router(cron.router, prefix="/api/v1/cron", tags=["cron"])
app.include_router(backups.router, prefix="/api/v1/backups", tags=["backups"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])


# Serve Frontend (if built)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dir):
    # Mount assets folder specifically to ensure MIME types are handled correctly
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # 1. Check if it's an API request (shouldn't be, but safe to check)
        if full_path.startswith("api/"):
            return {"error": "Not Found", "status": 404}

        # 2. Construct file path
        # If full_path is empty, it maps to root, but FastAPI usually sends "" for root if defined as /{path}
        # actually for root "/" it might not match catch-all depending on definition.
        # But we need to handle "index.html" mapping.

        target_file = full_path if full_path else "index.html"
        file_path = os.path.join(frontend_dir, target_file)

        # 3. If file exists (e.g. favicon.ico, vite.svg), serve it
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        # 4. Fallback to index.html for SPA (Vue Router)
        return FileResponse(os.path.join(frontend_dir, "index.html"))

else:
    @app.get("/")
    def read_root():
        return {"message": "s-panel API is running. Frontend build not found."}

import socket

def get_free_port(start_port: int = 21040, step: int = 10):
    port = start_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            port += step
            if port > 65535:
                raise RuntimeError("No available ports found.")

if __name__ == "__main__":
    if settings.SECRET_KEY == "changethis_to_a_secure_random_string_in_production":
        print("\n" + "="*60)
        print("WARNING: You are using the default SECRET_KEY!")
        print("Please update it in your .env file for security.")
        print("="*60 + "\n")

    try:
        port = get_free_port()
        print(f"Starting s-panel on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) # Reload false for prod entry point
    except Exception as e:
        print(f"Failed to start: {e}")

