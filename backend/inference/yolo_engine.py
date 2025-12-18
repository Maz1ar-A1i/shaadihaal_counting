import logging
import numpy as np
from ultralytics import YOLO
from shapely.geometry import Point, Polygon

logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        logger.info("Loading YOLOv8 Model (Nano)...")
        try:
            # Load YOLOv8n (nano) model - fast and sufficient for people counting
            self.model = YOLO('yolov8n.pt') 
            logger.info("YOLOv8 Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            self.model = None

    def detect_people(self, image_path: str, zones: list) -> int:
        """
        Runs detection on the image using YOLOv8.
        Filters results to count only people (class 0) that are inside the specified zones.
        """
        if self.model is None:
            logger.error("YOLO Model not loaded")
            return 0

        logger.info(f"Running YOLO inference on {image_path}")
        
        try:
            # Run inference
            # classes=[0] filters for 'person' class only
            results = self.model(image_path, classes=[0], verbose=False)
            
            count = 0
            
            # Parse results
            import cv2
            debug_img = cv2.imread(image_path)
            
            for r in results:
                # Iterate through detected boxes
                for box in r.boxes:
                    # Get box coordinates (xyxy)
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # Calculate center point of the person
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    # Normalize for zone check
                    img_h, img_w = r.orig_shape
                    norm_x = center_x / img_w
                    norm_y = center_y / img_h
                    
                    # Draw box
                    cv2.rectangle(debug_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.circle(debug_img, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)
                    
                    # Check zones
                    in_zone = False
                    if not zones:
                        in_zone = True
                        count += 1
                    else:
                        if self.is_point_in_zone((norm_x, norm_y), zones):
                             in_zone = True
                             count += 1
                    
                    # Label status
                    label = "Counted" if in_zone else "Ignored"
                    color = (0, 255, 0) if in_zone else (0, 0, 255)
                    cv2.putText(debug_img, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # Save debug image
            cv2.imwrite("debug_latest_detection.jpg", debug_img)
            
            return count
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            print(f"!!! YOLO INFERENCE ERROR: {e}") # VISIBLE DEBUG
            import traceback
            traceback.print_exc()
            return 0

    def is_point_in_zone(self, point, zone_points_list):
        """
        Checks if a normalized point (x, y) is inside any of the polygons in zone_points_list.
        """
        p = Point(point)
        for zone_pts in zone_points_list:
            if not zone_pts or len(zone_pts) < 3:
                continue
            
            # Create a polygon from the zone points
            # zone_pts is already [[x,y], [x,y]...]
            poly = Polygon(zone_pts)
            if poly.contains(p):
                return True
                
        return False

# Singleton instance
inference_engine = InferenceEngine()
