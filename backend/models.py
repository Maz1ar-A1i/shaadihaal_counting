from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    rtsp_url = Column(String)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    is_enabled = Column(Boolean, default=True)
    
    zones = relationship("Zone", back_populates="camera", cascade="all, delete-orphan")
    captures = relationship("CaptureResult", back_populates="camera")
    stats = relationship("CameraSessionStat", back_populates="camera")

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    name = Column(String)
    points = Column(JSON)  # List of [x, y] coordinates
    
    camera = relationship("Camera", back_populates="zones")

class CaptureSession(Base):
    __tablename__ = "capture_sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    captures = relationship("CaptureResult", back_populates="session")
    camera_stats = relationship("CameraSessionStat", back_populates="session")
    hall_stat = relationship("HallSessionStat", back_populates="session", uselist=False)

class CaptureResult(Base):
    __tablename__ = "capture_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("capture_sessions.id"))
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    image_path = Column(String)
    people_count = Column(Integer)
    captured_at = Column(DateTime, default=datetime.now)
    
    camera = relationship("Camera", back_populates="captures")
    session = relationship("CaptureSession", back_populates="captures")

class CameraSessionStat(Base):
    __tablename__ = "camera_session_stats"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("capture_sessions.id"))
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    average_count = Column(Float)
    
    camera = relationship("Camera", back_populates="stats")
    session = relationship("CaptureSession", back_populates="camera_stats")

class HallSessionStat(Base):
    __tablename__ = "hall_session_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("capture_sessions.id"))
    total_count = Column(Float) # Sum of averages
    recorded_at = Column(DateTime, default=datetime.now)
    
    session = relationship("CaptureSession", back_populates="hall_stat")
