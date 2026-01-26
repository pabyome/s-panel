from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from sqlmodel import Session
from app.models.database import create_db_and_tables, engine
from app.services.auth_service import AuthService
from app.api.v1 import auth, monitor, websites, firewall, supervisor, system, deployments, redis, cron

@asynccontextmanager
async def lifespan(app: FastAPI):
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

@app.get("/")
def read_root():
    return {"message": "s-panel API is running"}

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
    try:
        port = get_free_port()
        print(f"Starting s-panel on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) # Reload false for prod entry point
    except Exception as e:
        print(f"Failed to start: {e}")

