import shutil
import os
import sys

# Add backend to path to allow imports
sys.path.append(os.getcwd())

from backend.inference.sam3_engine import sam3_engine

# Path to uploaded image (NEW one)
src_image = "C:/Users/Mazhar Ali/.gemini/antigravity/brain/8ef626a0-5d33-414c-a166-5a9cf5d8adb6/uploaded_image_1767215102074.jpg"
dst_image = "test_sam_3.jpg"

print(f"Copying {src_image} to {dst_image}...")
shutil.copy(src_image, dst_image)

print("Running detection...")
try:
    # Empty zones list means count everything
    count = sam3_engine.detect_people(dst_image, [])
    print(f"Detection Result: {count} people found.")
    
    if os.path.exists("debug_latest_detection.jpg"):
        print("SUCCESS: debug_latest_detection.jpg created.")
    else:
        print("FAILURE: debug_latest_detection.jpg NOT created.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
