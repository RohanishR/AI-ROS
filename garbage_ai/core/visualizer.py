import cv2
from typing import List

class Visualizer:
    """
    Handles drawing bounding boxes, labels, and statistics on frames.
    """
    def __init__(self):
        # Define colors for our 5 categories + UNKNOWN
        self.colors = {
            "Plastic": (0, 165, 255),   # Orange
            "Paper": (255, 255, 0),     # Cyan
            "Metal": (128, 128, 128),   # Gray
            "Glass": (255, 0, 0),       # Blue
            "Organic": (0, 255, 0),     # Green
            "UNKNOWN": (0, 0, 255)      # Red
        }

    def draw(self, frame, detections: List[dict], fps: float = 0.0, inference_time_ms: float = 0.0):
        """
        Draws boxes, labels, and stats on the image in-place.
        """
        # Draw bounding boxes and labels
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            yolo_class = det['class_name']
            final_category = det['final_category']
            
            color = self.colors.get(final_category, self.colors["UNKNOWN"])
            
            # Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Label background
            label = f"{final_category} ({yolo_class} {conf*100:.0f}%)"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + tw, y1), color, -1)
            
            # Label text
            # Use black text if color is bright, else white. Simple heuristic:
            text_color = (0, 0, 0) if (color[0] + color[1] + color[2]) > 300 else (255, 255, 255)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
            
        # Draw statistics overlay
        overlay_text = [
            f"FPS: {fps:.1f}",
            f"Inference: {inference_time_ms:.1f} ms",
            f"Objects detected: {len(detections)}"
        ]
        
        y_offset = 30
        for text in overlay_text:
            # Shadow
            cv2.putText(frame, text, (12, y_offset + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            # Text
            cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_offset += 30
            
        return frame
