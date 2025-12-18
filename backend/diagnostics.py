import sys
import os
import time

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import CaptureResult, CaptureSession, Camera
from backend.services.scheduler_service import scheduler_service

def diagnose():
    print("=== DIAGNOSTIC START ===")
    
    # 1. Check Images Folder
    img_dir = "images"
    if os.path.exists(img_dir):
        files = os.listdir(img_dir)
        print(f"Image Directory '{img_dir}' exists. Contains {len(files)} files.")
        if len(files) > 0:
            print(f"Latest 3 files: {sorted(files)[-3:]}")
    else:
        print(f"!!! Image Directory '{img_dir}' DOES NOT EXIST.")

    # 2. Check Database
    db = SessionLocal()
    try:
        session = db.query(CaptureSession).filter(CaptureSession.is_completed == False).first()
        if session:
            print(f"Active Session: ID {session.id}, Started: {session.start_time}")
        else:
            print("No Active Session found.")
            
        # 3. Force Capture
        print(">>> Forcing Capture Cycle...")
        scheduler_service.check_and_run_cycle(force=True)
        print(">>> Capture Cycle Done.")
        
        # 4. Check Results
        results = db.query(CaptureResult).order_by(CaptureResult.captured_at.desc()).limit(3).all()
        print("Latest Capture Results:")
        for r in results:
            print(f" - [{r.captured_at}] Cam {r.camera_id}: Count {r.people_count}, Path: {r.image_path}")
            
    except Exception as e:
        print(f"!!! DIAGNOSTIC ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("=== DIAGNOSTIC END ===")

if __name__ == "__main__":
    diagnose()
