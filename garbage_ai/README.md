# Garbage Classification AI Module

This is the standalone AI perception module for the Smart Garbage Classification Robot. It detects garbage using a YOLO model and classifies it into 5 distinct categories:
`Plastic`, `Paper`, `Metal`, `Glass`, `Organic`.

The module is designed to run independently on a laptop (or Raspberry Pi) but is architected to cleanly integrate into a ROS2 node in the future.

## 1. Project Overview & Architecture

### Core Components
- **GarbageDetector (`core/detector.py`)**: A wrapper around Ultralytics YOLO. Takes a numpy array frame and outputs bounding boxes, raw classes, and confidences. Independent of media sources.
- **WasteClassifier (`core/classifier.py`)**: Loads configuration mappings. Takes raw YOLO outputs, applies a confidence threshold, and groups specific objects (e.g. `plastic_bottle`, `clear_plastic_bottle`) into the final 5 target categories (or `UNKNOWN` if below threshold).
- **Visualizer (`core/visualizer.py`)**: Handles OpenCV overlay drawing for bounding boxes, text labels, and real-time FPS statistics.
- **Main Executable (`main.py`)**: Glues the components together. Connects to webcams, images, or video files.

### ROS2 Future Integration
Because the AI logic is decoupled from `main.py`'s camera polling loop, migrating to ROS2 is straightforward:
1. Create a `garbage_detection_node.py`.
2. Subscribe to `/camera/image_raw` using `cv_bridge`.
3. In the callback, run `detections = detector.predict(cv_frame)` and `classifier.process_detections(detections)`.
4. Publish the output to a custom topic like `/waste_category`.

## 2. Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 3. Configuration

The configuration file is located at `config/config.yaml`.
- **Model Size**: By default it uses `yolov8n.pt`. You can change this to your custom trained weights (e.g., `outputs/train_run/weights/best.pt`).
- **Confidence Threshold**: Defined under `inference.confidence_threshold`.
- **Category Mapping**: Define which YOLO classes belong to which of the 5 final categories under `category_mapping`.

## 4. Inference (Using the Module)

You can run detection on various sources using `main.py`. Results (annotated images/videos) are saved to the `outputs/` directory.

### Webcam Detection
```bash
python main.py --source webcam
```
Press `q` to quit the webcam feed.

### Image Detection
```bash
python main.py --source /path/to/test_image.jpg
```

### Video Detection
```bash
python main.py --source /path/to/test_video.mp4
```

## 5. Dataset Preparation (TACO)

If you wish to train a custom model from scratch using the TACO dataset:
1. Run the annotation conversion script:
   ```bash
   python scripts/prepare_taco.py --dest dataset/
   ```
2. **Important**: The images themselves must be downloaded using the official TACO repo scripts as they are distributed across multiple URLs. See [TACO GitHub](https://github.com/pedropro/TACO) for details.

## 6. Model Training & Validation

Once you have a prepared YOLO dataset `data.yaml`:

### Training
```bash
python scripts/train.py --data dataset/data.yaml --epochs 50 --batch 16
```
This uses the model defined in `config.yaml` as the starting weights. Results are saved in `outputs/train_run/`.

### Validation
To validate a trained model:
```bash
python scripts/validate.py --weights outputs/train_run/weights/best.pt --data dataset/data.yaml
```

## 7. Testing
Run logic tests for the classification mapping and thresholds:
```bash
python -m unittest discover tests/
```
