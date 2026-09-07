import argparse
import yaml
from ultralytics import YOLO

def train(config_path, data_yaml, epochs, batch_size):
    """
    Train YOLOv8 on a custom dataset.
    """
    # Load model configuration to know which base model to use
    try:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
            model_path = cfg.get('model', {}).get('path', 'yolov8n.pt')
            imgsz = cfg.get('model', {}).get('img_size', 640)
    except Exception as e:
        print(f"Failed to read config: {e}. Defaulting to yolov8n.pt")
        model_path = 'yolov8n.pt'
        imgsz = 640

    print(f"Initializing YOLO model from {model_path}...")
    model = YOLO(model_path)

    print(f"Starting training on dataset {data_yaml} for {epochs} epochs...")
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        project='outputs',
        name='train_run',
        exist_ok=True # Overwrite if exists, or change to False to create train_run2, etc.
    )
    
    print("Training complete. Results saved in outputs/train_run/")
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train Garbage Detection Model")
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to main config')
    parser.add_argument('--data', type=str, required=True, help='Path to dataset YAML file (e.g., dataset/data.yaml)')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    
    args = parser.parse_args()
    train(args.config, args.data, args.epochs, args.batch)
