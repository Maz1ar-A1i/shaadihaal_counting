from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Shared ---
class MessageResponse(BaseModel):
    message: str

# --- Camera Schemas ---
class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    is_enabled: Optional[bool] = True

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_enabled: Optional[bool] = None

class CameraOut(CameraBase):
    id: int

    class Config:
        from_attributes = True

# --- Zone Schemas ---
class ZoneBase(BaseModel):
    name: str
    points: List[List[float]]  # List of [x, y]

class ZoneCreate(ZoneBase):
    camera_id: int

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    points: Optional[List[List[float]]] = None

class ZoneOut(ZoneBase):
    id: int
    camera_id: int

    class Config:
        from_attributes = True

# --- Stats/History Schemas ---
class CaptureResultOut(BaseModel):
    id: int
    camera_id: int
    image_path: str
    people_count: int
    captured_at: datetime
    
    class Config:
        from_attributes = True

class SessionStatOut(BaseModel):
    session_id: int
    start_time: datetime
    end_time: Optional[datetime]
    total_hall_count: Optional[float]
    
    class Config:
        from_attributes = True
