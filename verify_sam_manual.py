import sys
import os
import cv2
import numpy as np

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.inference.sam_engine import sam_engine

def test_sam_integration():
    print("Testing SAM 3 Integration...")
    
    # Create a dummy image if not exists
    img_path = "test_sam_3.jpg"
    if not os.path.exists(img_path):
        img = np.zeros((640, 640, 3), dtype=np.uint8)
        # Draw a person-like shape (simplified)
        cv2.circle(img, (320, 200), 50, (255, 255, 255), -1) # Head
        cv2.rectangle(img, (270, 250), (370, 450), (255, 255, 255), -1) # Body
        cv2.imwrite(img_path, img)
        print(f"Created dummy test image: {img_path}")
        
    # Run detection
    print(f"Running detection on {img_path}")
    count = sam_engine.detect_people(img_path, zones=[])
    
    print(f"Detection Result: {count} people found.")
    
if __name__ == "__main__":
    test_sam_integration()
