import time
from ultralytics import YOLO

class GarbageDetector:
    """
    Wrapper around YOLO for garbage detection.
    Independent of ROS2 and specific camera implementations.
    """
    def __init__(self, model_path: str, device: str = "cuda"):
        # Load the YOLO model (will download yolov8n.pt if not exists and is requested)
        self.model = YOLO(model_path)
        self.device = device
        
        # Warmup
        try:
            self.model.info() # Basic check
        except Exception as e:
            print(f"Failed to load model {model_path}: {e}")

    def predict(self, frame):
        """
        Runs YOLO inference on a single BGR frame (numpy array).
        Returns a list of detections: [{"bbox": (x1, y1, x2, y2), "class_name": str, "confidence": float}]
        and the inference time in ms.
        """
        start_time = time.time()
        
        # Run inference
        # verbose=False to keep the console clean for FPS stats
        results = self.model.predict(frame, device=self.device, verbose=False)
        
        inference_time_ms = (time.time() - start_time) * 1000
        
        detections = []
        if len(results) > 0:
            result = results[0]
            names = result.names # dictionary of class ID to class Name
            boxes = result.boxes
            
            for box in boxes:
                # Extract coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = names[cls_id]
                
                detections.append({
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                    "class_name": cls_name,
                    "confidence": conf
                })
                
        return detections, inference_time_ms
