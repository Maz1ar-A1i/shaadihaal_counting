from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Camera
from ..schemas import CameraCreate, CameraUpdate, CameraOut, MessageResponse

router = APIRouter(prefix="/cameras", tags=["cameras"])

@router.get("/", response_model=List[CameraOut])
def get_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()

@router.post("/", response_model=CameraOut)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.put("/{camera_id}", response_model=CameraOut)
def update_camera(camera_id: int, camera: CameraUpdate, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    update_data = camera.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_camera, key, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.delete("/{camera_id}", response_model=MessageResponse)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted successfully"}

from fastapi.responses import StreamingResponse
import cv2
import io
from ..services.camera_service import CameraService

@router.get("/{camera_id}/preview")
def get_camera_preview(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    frame, err = CameraService.capture_frame(db_camera.rtsp_url)
    if err or frame is None:
        # Return a placeholder or error image
        return Response(status_code=503, content="Stream unavailable")
    
    # Encode to JPEG
    _, img_encoded = cv2.imencode('.jpg', frame)
    return Response(content=img_encoded.tobytes(), media_type="image/jpeg")
