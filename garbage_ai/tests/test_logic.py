import unittest
import os
import yaml
from core.classifier import WasteClassifier

class TestWasteClassifier(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy config for testing
        self.config_path = "test_config.yaml"
        config_data = {
            "inference": {"confidence_threshold": 0.50},
            "category_mapping": {
                "Plastic": ["plastic_bottle", "plastic_bag"],
                "Paper": ["newspaper", "cardboard"],
                "Metal": ["aluminum_can"],
                "Glass": ["glass_bottle"],
                "Organic": ["banana_peel"]
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)
            
        self.classifier = WasteClassifier(self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_high_confidence_mapping(self):
        # Test exact mapping
        cat = self.classifier.classify("plastic_bottle", 0.90)
        self.assertEqual(cat, "Plastic")
        
        cat = self.classifier.classify("aluminum_can", 0.85)
        self.assertEqual(cat, "Metal")

    def test_low_confidence_threshold(self):
        # Test that low confidence results in UNKNOWN despite mapping existing
        cat = self.classifier.classify("plastic_bottle", 0.40)
        self.assertEqual(cat, "UNKNOWN")

    def test_unmapped_class(self):
        # Test that unmapped classes result in UNKNOWN
        cat = self.classifier.classify("random_object", 0.99)
        self.assertEqual(cat, "UNKNOWN")
        
    def test_process_detections_batch(self):
        # Test the batch processing
        detections = [
            {"class_name": "newspaper", "confidence": 0.8},
            {"class_name": "plastic_bag", "confidence": 0.3}, # Low conf
            {"class_name": "banana_peel", "confidence": 0.6}
        ]
        
        processed = self.classifier.process_detections(detections)
        
        self.assertEqual(processed[0]["final_category"], "Paper")
        self.assertEqual(processed[1]["final_category"], "UNKNOWN")
        self.assertEqual(processed[2]["final_category"], "Organic")

if __name__ == '__main__':
    unittest.main()
