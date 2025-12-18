from ultralytics import YOLO
import cv2
import numpy as np
import os

def test_yolo():
    print("Testing YOLOv8...")
    try:
        model = YOLO("yolov8n.pt")
        print("Model loaded.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    img_path = "test_image.jpg"
    if not os.path.exists(img_path):
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.rectangle(img, (100, 100), (300, 300), (255, 255, 255), -1)
        cv2.imwrite(img_path, img)
        print("Created test image.")

    print(f"Running inference on {img_path}...")
    results = model(img_path, classes=[0]) # 0 = person
    
    count = 0
    for r in results:
        count += len(r.boxes)
        print(f"Detected {len(r.boxes)} people.")
        for box in r.boxes:
            print(f"Box: {box.xyxy[0].tolist()}, Conf: {box.conf[0].item()}")

if __name__ == "__main__":
    test_yolo()
