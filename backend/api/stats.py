from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import csv
import io

from ..database import get_db
from ..models import CaptureSession, HallSessionStat, CameraSessionStat, Camera, CaptureResult
from ..schemas import SessionStatOut

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/live")
def get_live_stats(db: Session = Depends(get_db)):
    """
    Returns the most recent captured count for the active session.
    """
    # Find active session
    session = db.query(CaptureSession).filter(CaptureSession.is_completed == False).first()
    if not session:
        return {"live_count": 0}
        
    # Get latest result for this session
    # We want the SUM of latest counts from all active cameras
    cams = db.query(Camera).filter(Camera.is_enabled == True).all()
    total_live = 0
    
    last_updated = None
    
    for cam in cams:
        last = db.query(CaptureResult).filter(
            CaptureResult.session_id == session.id,
            CaptureResult.camera_id == cam.id
        ).order_by(CaptureResult.captured_at.desc()).first()
        
        if last:
            total_live += last.people_count
            if not last_updated or last.captured_at > last_updated:
                last_updated = last.captured_at
            
    return {
        "live_count": total_live,
        "last_updated": last_updated
    }



@router.get("/history", response_model=List[SessionStatOut])
def get_history(db: Session = Depends(get_db)):
    """
    Returns completed sessions with their total hall counts.
    """
    sessions = db.query(CaptureSession).order_by(CaptureSession.start_time.desc()).all()
    
    result = []
    for s in sessions:
        if s.is_completed:
            total = s.hall_stat.total_count if s.hall_stat else 0
        else:
            # For active session, calculate rough total from latest captures
            # (Similar logic to live stats, but maybe just use what we have)
            cams = db.query(Camera).filter(Camera.is_enabled == True).all()
            total = 0
            for cam in cams:
                last = db.query(CaptureResult).filter(
                    CaptureResult.session_id == s.id,
                    CaptureResult.camera_id == cam.id
                ).order_by(CaptureResult.captured_at.desc()).first()
                if last:
                    total += last.people_count
        
        result.append({
            "session_id": s.id,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "total_hall_count": total
        })
    return result

@router.get("/export")
def export_csv(db: Session = Depends(get_db)):
    """
    Exports all completed session data to CSV.
    Format: Session ID, Start Time, End Time, Camera Name, Average Count
    """
    sessions = db.query(CaptureSession).filter(CaptureSession.is_completed == True).order_by(CaptureSession.start_time.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Session ID", "Start Time", "End Time", "Total Hall Count", "Camera Name", "Camera Average"])
    
    for s in sessions:
        start_str = s.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_str = s.end_time.strftime("%Y-%m-%d %H:%M:%S") if s.end_time else ""
        total = s.hall_stat.total_count if s.hall_stat else 0
        
        # Get per-camera stats
        cam_stats = db.query(CameraSessionStat).filter(CameraSessionStat.session_id == s.id).all()
        
        if not cam_stats:
            # Entry without camera details
            writer.writerow([s.id, start_str, end_str, total, "N/A", "N/A"])
        else:
            for cs in cam_stats:
                cam_name = cs.camera.name if cs.camera else f"Cam {cs.camera_id}"
                writer.writerow([s.id, start_str, end_str, total, cam_name, cs.average_count])
                
    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=stats.csv"})
