import cv2
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CameraService:
    @staticmethod
    def capture_frame(rtsp_url: str) -> Optional[tuple]:
        """
        Captures a single frame from the RTSP stream.
        Returns (frame, error_message).
        """
        try:
            # Handle numeric camera indices (e.g. "0", "1") for local webcams
            source = rtsp_url
            if str(rtsp_url).isdigit():
                source = int(rtsp_url)

            # Open video stream
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                return None, f"Failed to open stream: {rtsp_url}"
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None, "Failed to read frame"
            
            return frame, None
        except Exception as e:
            logger.error(f"Error capturing frame from {rtsp_url}: {e}")
            return None, str(e)

    @staticmethod
    def save_frame(frame, output_path: str):
        cv2.imwrite(output_path, frame)
