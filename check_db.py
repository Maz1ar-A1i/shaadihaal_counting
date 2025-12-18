from backend.database import SessionLocal
from backend.models import CaptureResult, CaptureSession, Camera
from backend.services.scheduler_service import scheduler_service
import time

def check_db():
    # print("--- TRIGGERING FORCE RUN ---")
    # # This simulates exactly what the scheduler does
    # scheduler_service.check_and_run_cycle(force=True)
    # print("--- FORCE RUN ACTION COMPLETED (Check logs/images) ---")
    # time.sleep(2) # Wait for async/threads if any (though currently sync)

    db = SessionLocal()
    print("\n--- Cameras ---")
    cams = db.query(Camera).all()
    for c in cams:
        print(f"ID: {c.id}, Name: {c.name}, Enabled: {c.is_enabled}, URL: {c.rtsp_url}")
        for z in c.zones:
            print(f"  - Zone: {z.name}, Points: {len(z.points)}")

    print("\n--- Latest Capture Results (Last 5) ---")
    results = db.query(CaptureResult).order_by(CaptureResult.captured_at.desc()).limit(5).all()
    if not results:
        print("No results found.")
    for r in results:
        print(f"Time: {r.captured_at}, Session: {r.session_id}, Cam: {r.camera_id}, Count: {r.people_count}, Path: {r.image_path}")

    print("\n--- Active Session ---")
    active = db.query(CaptureSession).filter(CaptureSession.is_completed == False).first()
    if active:
        print(f"ID: {active.id}, Start: {active.start_time}")
    else:
        print("No active session.")

    db.close()

if __name__ == "__main__":
    check_db()
