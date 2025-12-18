import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, Scheduler, etc.
    logger.info("Starting up Multi-Camera People Counting System...")
    
    # Create DB Tables
    from .database import engine, Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")
    
    # Start Scheduler
    from .services.scheduler_service import scheduler_service
    logger.info("Scheduler started via explicit import.")

    yield
    # Shutdown: Clean up resources
    logger.info("Shutting down...")

# Changed app title as per instruction
app = FastAPI(title="ShadiHaal Analytics", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .api import cameras, zones, stats
app.include_router(cameras.router)
app.include_router(zones.router)
app.include_router(stats.router)

@app.post("/debug/trigger")
async def trigger_detection():
    # Force run the scheduler cycle immediately
    await scheduler_service.check_and_run_cycle(force=True)
    return {"status": "triggered"}

@app.get("/")
def read_root():
    return {"message": "System is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
