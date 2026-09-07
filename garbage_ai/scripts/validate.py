import argparse
from ultralytics import YOLO

def validate(model_path, data_yaml):
    """
    Validates a trained YOLO model against the validation split.
    """
    print(f"Loading model {model_path}...")
    model = YOLO(model_path)
    
    print(f"Running validation on {data_yaml}...")
    metrics = model.val(
        data=data_yaml,
        project='outputs',
        name='val_run',
        exist_ok=True
    )
    
    print("Validation complete.")
    print(f"mAP50-95: {metrics.box.map:.3f}")
    print(f"mAP50: {metrics.box.map50:.3f}")
    print("Confusion matrix and graphs saved in outputs/val_run/")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate Garbage Detection Model")
    parser.add_argument('--weights', type=str, required=True, help='Path to trained weights (e.g., outputs/train_run/weights/best.pt)')
    parser.add_argument('--data', type=str, required=True, help='Path to dataset YAML file')
    
    args = parser.parse_args()
    validate(args.weights, args.data)
