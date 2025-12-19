from fastapi import APIRouter
from ..services.scheduler_service import scheduler_service

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status")
def get_system_status():
    return {
        "is_paused": scheduler_service.is_paused
    }

@router.post("/pause")
def pause_system():
    scheduler_service.pause()
    return {"status": "paused", "is_paused": True}

@router.post("/resume")
def resume_system():
    scheduler_service.resume()
    return {"status": "resumed", "is_paused": False}
