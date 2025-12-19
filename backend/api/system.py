from fastapi import APIRouter
from ..services.scheduler_service import scheduler_service

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status")
def get_system_status():
    return {
        "is_paused": scheduler_service.is_paused,
        "scheduled_start_time": scheduler_service.scheduled_start_time
    }

@router.post("/pause")
def pause_system():
    scheduler_service.pause()
    return {"status": "paused", "is_paused": True}

@router.post("/resume")
def resume_system():
    scheduler_service.resume()
    return {"status": "resumed", "is_paused": False}

from pydantic import BaseModel
class ScheduleRequest(BaseModel):
    time: str | None = None

@router.post("/schedule")
def set_schedule(req: ScheduleRequest):
    scheduler_service.set_schedule(req.time)
    return {"status": "scheduled", "time": req.time}
