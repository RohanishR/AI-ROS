import yaml
from typing import Dict, List, Optional

class WasteClassifier:
    """
    Maps YOLO detected object classes to our 5 final categories
    and applies a confidence threshold.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.confidence_threshold = 0.60
        self.mapping: Dict[str, str] = {}
        
        self.load_config()

    def load_config(self):
        """Loads thresholds and category mappings from config.yaml"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            self.confidence_threshold = config.get('inference', {}).get('confidence_threshold', 0.60)
            
            category_mapping = config.get('category_mapping', {})
            
            # Flatten the mapping for O(1) lookups: {'plastic_bottle': 'Plastic', ...}
            for final_category, yolo_classes in category_mapping.items():
                for cls in yolo_classes:
                    self.mapping[cls] = final_category
                    
        except Exception as e:
            print(f"Error loading config {self.config_path}: {e}")
            print("Falling back to default mapping and threshold 0.60")

    def classify(self, yolo_class_name: str, confidence: float) -> str:
        """
        Applies mapping and threshold to determine the final category.
        If confidence < threshold -> UNKNOWN
        If class not in mapping -> UNKNOWN (or could be mapped differently, but safe is UNKNOWN)
        """
        if confidence < self.confidence_threshold:
            return "UNKNOWN"
            
        final_category = self.mapping.get(yolo_class_name, "UNKNOWN")
        return final_category

    def process_detections(self, detections: List[dict]) -> List[dict]:
        """
        Processes a list of raw YOLO detections and adds the 'final_category' field.
        """
        for det in detections:
            det['final_category'] = self.classify(det['class_name'], det['confidence'])
        return detections
