import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os

from ..database import SessionLocal
from ..models import Camera, CaptureSession, CaptureResult, CameraSessionStat, HallSessionStat
from .camera_service import CameraService
from ..inference.sam3_engine import sam3_engine
import csv

logger = logging.getLogger(__name__)

# Make sure we print to console as well for the user
# Make sure we print to console as well for the user
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler_debug.log"),
        logging.StreamHandler()
    ]
)

IMAGE_DIR = "images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

CSV_LOG_FILE = "live_captures.csv"

print("--- [DEBUG] SchedulerService: Importing... ---")
class SchedulerService:
    def __init__(self):
        print("--- [DEBUG] SchedulerService: Initializing Instance... ---")
        self.scheduler = BackgroundScheduler()
        self.is_paused = False
        self.scheduled_start_time = None # Format "HH:MM"
        self.capture_interval_minutes = 5 # Default 5 minutes
        # Use 'cron' to trigger exactly at the top of every minute (:00 seconds)
        # This ensures we catch the hh:mm transition instantly
        self.scheduler.add_job(self.check_and_run_cycle, 'cron', second='0', next_run_time=datetime.now())
        
        # Initialize CSV header if file doesn't exist
        if not os.path.exists(CSV_LOG_FILE):
             with open(CSV_LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "SessionID", "CameraID", "Count", "ImagePath"])
        
    def is_session_active(self):
        """Check if any session is currently active (not completed)."""
        db = SessionLocal()
        try:
             return db.query(CaptureSession).filter(CaptureSession.is_completed == False).count() > 0
        finally:
            db.close()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")
    
    def pause(self):
        logger.info("System Paused")
        self.is_paused = True
        
    def resume(self):
        logger.info("System Resumed")
        self.is_paused = False

    def set_schedule(self, time_str: str):
        """Set auto-start time in HH:MM format"""
        self.scheduled_start_time = time_str
        logger.info(f"Scheduled start time set to {time_str}")

    def set_interval(self, minutes: int):
        """Set capture interval in minutes"""
        if minutes < 1:
            minutes = 1
        self.capture_interval_minutes = minutes
        logger.info(f"Capture interval set to {minutes} minutes")

    def check_and_run_cycle(self, force: bool = False):
        """
        Runs every minute.
        Checks if we need to start a session or perform a capture within an active session.
        If force=True, ignores time gaps.
        """
        if self.is_paused and not force:
            # Check if we should auto-start
            current_time = datetime.now().strftime("%H:%M")
            if self.scheduled_start_time:
                print(f"--- [DEBUG] PAUSED Loop. Current: {current_time} | Scheduled: {self.scheduled_start_time} ---")
                
                if current_time == self.scheduled_start_time:
                    print(f"--- [DEBUG] Auto-Start MATCHED! Resuming... ---")
                    self.resume()
                    # We continue execution below (don't return)
                else:
                    # Only print every once in a while to avoid spam? No, spam is good for debug right now.
                    # print(f"[{datetime.now().strftime('%H:%M:%S')}] SCHEDULER PAUSED (Waiting for {self.scheduled_start_time})")
                    return
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] SCHEDULER PAUSED (No Schedule)")
                return

        db = SessionLocal()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SCHEDULER TICK CHECK") # Visible heartbeat
        try:
            # 1. Check for active session
            active_session = db.query(CaptureSession).filter(CaptureSession.is_completed == False).first()
            
            if not active_session:
                return # Auto-start disabled
                # No active session. Should we start one?
                # For demo, let's start one if none exists (Continuous loops with gaps?)
                # Or maybe every 30 minutes?
                # Let's enforce a rule: Start new session if last one finished > 5 mins ago? 
                # Simplest: Start immediately if none active (Continuous Measurement).
                
                # Check if we have any cameras
                cameras = db.query(Camera).filter(Camera.is_enabled == True).all()
                if not cameras:
                    logger.info("No enabled cameras. Skipping session start.")
                    return

                logger.info("Starting new Capture Session")
                new_session = CaptureSession(start_time=datetime.now())
                db.add(new_session)
                db.commit()
                db.refresh(new_session)
                
                self.perform_capture(db, new_session)
                
            else:
                # Active session exists. Check if it's time for next capture.
                last_capture = db.query(CaptureResult).filter(CaptureResult.session_id == active_session.id)\
                                 .order_by(CaptureResult.captured_at.desc()).first()
                
                if not last_capture:
                    # Should not happen if created correctly, but recover
                    self.perform_capture(db, active_session)
                else:
                    # Check gap
                    time_since_last = datetime.now() - last_capture.captured_at
                    # Requirement: configurable gap
                    GAP_MINUTES = self.capture_interval_minutes 
                                        
                    if force or time_since_last >= timedelta(minutes=GAP_MINUTES):
                        # check how many we have
                        count = db.query(CaptureResult).filter(CaptureResult.session_id == active_session.id).count()
                        # Each camera produces 1 result per capture event. 
                        # We need to count "events". Distinct timestamps?
                        # Since we capture all cameras at once, dividing by num_cameras gives events?
                        # Safe way: Count distinct timestamps or just track "rounds".
                        
                        # Let's count totals and divide by camera count, or just assume we do 5 rounds.
                        cameras = db.query(Camera).filter(Camera.is_enabled == True).all()
                        num_cameras = len(cameras)
                        if num_cameras == 0:
                             active_session.is_completed = True
                             db.commit()
                             return

                        current_images = db.query(CaptureResult).filter(CaptureResult.session_id == active_session.id).count()
                        rounds_done = current_images // num_cameras
                        
                        if rounds_done >= 5:
                            # We are done. Finalize.
                            self.finalize_session(db, active_session)
                        else:
                            self.perform_capture(db, active_session)
                            
        except Exception as e:
            logger.error(f"Scheduler Error: {e}")
            print(f"!!! SCHEDULER ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()

    def perform_capture(self, db: Session, session: CaptureSession):
        logger.info(f"Performing capture for Session {session.id}")
        cameras = db.query(Camera).filter(Camera.is_enabled == True).all()
        
        for cam in cameras:
            # Capture Frame
            frame, err = CameraService.capture_frame(cam.rtsp_url)
            if err:
                logger.error(f"Failed to capture cam {cam.id}: {err}")
                continue # Skip or record error
            
            # Save Image
            filename = f"sess_{session.id}_cam_{cam.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(IMAGE_DIR, filename)
            CameraService.save_frame(frame, filepath)
            
            # Run Inference
            # Get zones
            zones = [z.points for z in cam.zones]
            count = sam3_engine.detect_people(filepath, zones)
            
            # Save Result
            result = CaptureResult(
                session_id=session.id,
                camera_id=cam.id,
                image_path=filepath,
                people_count=count,
                captured_at=datetime.now()
            )
            db.add(result)
            
            # Append to Live CSV
            try:
                with open(CSV_LOG_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    # "Timestamp", "SessionID", "CameraID", "Count", "ImagePath"
                    writer.writerow([
                        result.captured_at.strftime("%Y-%m-%d %H:%M:%S"),
                        session.id,
                        cam.id,
                        count,
                        filepath
                    ])
                    f.flush() # Ensure it's written immediately
                    os.fsync(f.fileno()) # Force write to disk
            except Exception as e:
                logger.error(f"Failed to write to CSV: {e}")

        
        db.commit()
        
        # Check if this was the 5th round
        total_captures = db.query(CaptureResult).filter(CaptureResult.session_id == session.id).count()
        num_cameras = len(cameras)
        if total_captures >= 5 * num_cameras:
             self.finalize_session(db, session)

    def finalize_session(self, db: Session, session: CaptureSession):
        logger.info(f"Finalizing Session {session.id}")
        session.end_time = datetime.now()
        session.is_completed = True
        
        # Compute Stats
        cameras = db.query(Camera).all()
        total_hall_count = 0
        
        for cam in cameras:
            results = db.query(CaptureResult).filter(
                CaptureResult.session_id == session.id,
                CaptureResult.camera_id == cam.id
            ).all()
            
            if not results:
                continue
                
            avg = sum([r.people_count for r in results]) / len(results)
            
            stat = CameraSessionStat(
                session_id=session.id,
                camera_id=cam.id,
                average_count=avg
            )
            db.add(stat)
            total_hall_count += avg
            
        hall_stat = HallSessionStat(
            session_id=session.id,
            total_count=total_hall_count
        )
        db.add(hall_stat)
        db.commit()
    def start_new_session(self):
        """Manually start a new session."""
        db = SessionLocal()
        try:
            # Check if one exists
            active = db.query(CaptureSession).filter(CaptureSession.is_completed == False).first()
            if active:
                logger.warning("Session already active.")
                return False

            # Check cameras
            cameras = db.query(Camera).filter(Camera.is_enabled == True).all()
            if not cameras:
                logger.error("No enabled cameras. Cannot start.")
                return False

            logger.info("Starting new Capture Session (Manual)")
            new_session = CaptureSession(start_time=datetime.now())
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            # Immediate capture
            # Ensure system is running (Auto-Resume)
            if self.is_paused:
                self.resume()

            self.perform_capture(db, new_session)
            return True
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return False
        finally:
            db.close()

    def force_finish_session(self):
        """Manually stop and finalize ALL active sessions."""
        db = SessionLocal()
        try:
            active_sessions = db.query(CaptureSession).filter(CaptureSession.is_completed == False).all()
            if active_sessions:
                logger.info(f"Force finishing {len(active_sessions)} active sessions via user request")
                for session in active_sessions:
                     self.finalize_session(db, session)
                return True
            return False
        except Exception as e:
            logger.error(f"Error force finishing session: {e}")
            return False
        finally:
            db.close()

scheduler_service = SchedulerService()
