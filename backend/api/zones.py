from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Zone, Camera
from ..schemas import ZoneCreate, ZoneUpdate, ZoneOut, MessageResponse

router = APIRouter(prefix="/zones", tags=["zones"])

@router.get("/camera/{camera_id}", response_model=List[ZoneOut])
def get_zones_by_camera(camera_id: int, db: Session = Depends(get_db)):
    return db.query(Zone).filter(Zone.camera_id == camera_id).all()

@router.post("/", response_model=ZoneOut)
def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == zone.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    db_zone = Zone(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.put("/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: int, zone: ZoneUpdate, db: Session = Depends(get_db)):
    db_zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    update_data = zone.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_zone, key, value)
    
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.delete("/{zone_id}", response_model=MessageResponse)
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    db_zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    db.delete(db_zone)
    db.commit()
    return {"message": "Zone deleted successfully"}
