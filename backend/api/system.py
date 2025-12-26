from fastapi import APIRouter
from ..services.scheduler_service import scheduler_service

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status")
def get_system_status():
    return {
        "is_paused": scheduler_service.is_paused,
        "scheduled_start_time": scheduler_service.scheduled_start_time,
        "capture_interval_minutes": scheduler_service.capture_interval_minutes,
        "is_session_active": scheduler_service.is_session_active()
    }

@router.post("/pause")
def pause_system():
    scheduler_service.pause()
    return {"status": "paused", "is_paused": True}

@router.post("/resume")
def resume_system():
    scheduler_service.resume()
    return {"status": "resumed", "is_paused": False}

@router.post("/stop_session")
def stop_session():
    """Ends the current active session properly."""
    success = scheduler_service.force_finish_session()
    return {"status": "session_stopped" if success else "no_active_session"}

@router.post("/start_session")
def start_session():
    """Manually starts a new session."""
    success = scheduler_service.start_new_session()
    if success:
        return {"status": "session_started"}
    else:
        # returns 400 or just status error
        return {"status": "error", "message": "Could not start session. Check logs (maybe active session exists or no cameras)."}

from pydantic import BaseModel
class ScheduleRequest(BaseModel):
    time: str | None = None

@router.post("/schedule")
def set_schedule(req: ScheduleRequest):
    scheduler_service.set_schedule(req.time)
    return {"status": "scheduled", "time": req.time}

class IntervalRequest(BaseModel):
    minutes: int

@router.post("/interval")
def set_interval(req: IntervalRequest):
    scheduler_service.set_interval(req.minutes)
    return {"status": "interval_set", "minutes": req.minutes}
