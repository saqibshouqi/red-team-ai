"""
Main FastAPI application
"""

import os
import sys

# Add root directory to path (where agents/ is located)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

import logging

from api.agents import router as agents_router
from api.experiments import router as experiments_router
from config import settings
from database import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Production-grade platform for evaluating Role-Playing Language Agents using adversarial testing",
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.version}")

    # Initialize database
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "api": settings.api_prefix,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
app.include_router(experiments_router, prefix=settings.api_prefix)
app.include_router(agents_router, prefix=settings.api_prefix)

# Serve React frontend from frontend/dist/ if it exists (production build)
_frontend_dist = os.path.join(root_dir, "frontend", "dist")
if os.path.isdir(_frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(_frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index = os.path.join(_frontend_dist, "index.html")
        return FileResponse(index)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=settings.debug, log_level="info"
    )
