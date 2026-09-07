import argparse
import cv2
import time
import os
from core.detector import GarbageDetector
from core.classifier import WasteClassifier
from core.visualizer import Visualizer

def process_image(source_path: str, detector, classifier, visualizer):
    print(f"Processing image: {source_path}")
    frame = cv2.imread(source_path)
    if frame is None:
        print(f"Error: Could not read image {source_path}")
        return

    detections, inf_time = detector.predict(frame)
    detections = classifier.process_detections(detections)
    
    # Print results to console
    print("-" * 15)
    for det in detections:
        print(f"Object: {det['class_name']}")
        print(f"Category: {det['final_category']}")
        print(f"Confidence: {det['confidence']*100:.0f}%")
        print("-" * 15)

    frame = visualizer.draw(frame, detections, fps=0, inference_time_ms=inf_time)
    
    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", os.path.basename(source_path))
    cv2.imwrite(out_path, frame)
    print(f"Saved annotated image to {out_path}")

def process_video_stream(source, detector, classifier, visualizer):
    """Handles both webcam and video files"""
    is_webcam = str(source).lower() == 'webcam'
    
    if is_webcam:
        cap = cv2.VideoCapture(0)
        print("Starting webcam... Press 'q' to quit.")
    else:
        cap = cv2.VideoCapture(source)
        print(f"Processing video: {source}")
        
        # Setup video writer
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_in = int(cap.get(cv2.CAP_PROP_FPS))
        os.makedirs("outputs", exist_ok=True)
        out_path = os.path.join("outputs", os.path.basename(source))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = cv2.VideoWriter(out_path, fourcc, fps_in, (width, height))

    if not cap.isOpened():
        print(f"Error: Could not open video source {source}")
        return

    fps_tracker = 0
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Inference
        detections, inf_time = detector.predict(frame)
        
        # Classification
        detections = classifier.process_detections(detections)
        
        # FPS calc
        curr_time = time.time()
        fps_tracker = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        # Print high confidence detections occasionally (or every frame if needed)
        # For terminal clarity, we print only if we detect something.
        if is_webcam and len(detections) > 0:
            # simple clear screen equivalent for cleaner output
            print("\033[H\033[J", end="") 
            print("-" * 15)
            for det in detections:
                print(f"Object: {det['class_name']}")
                print(f"Category: {det['final_category']}")
                print(f"Confidence: {det['confidence']*100:.0f}%")
            print("-" * 15)

        # Visualization
        frame = visualizer.draw(frame, detections, fps=fps_tracker, inference_time_ms=inf_time)
        
        if is_webcam:
            cv2.imshow('Garbage Classification AI', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            out_video.write(frame)

    cap.release()
    if is_webcam:
        cv2.destroyAllWindows()
    else:
        out_video.release()
        print(f"Saved annotated video to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Smart Garbage Classification AI Module")
    parser.add_argument('--source', type=str, required=True, 
                        help="Source: 'webcam', path to image (.jpg/.png), or path to video (.mp4)")
    args = parser.parse_args()

    # Initialize AI Core Components
    # Hardcoded config path for standalone testing. Later ROS2 can pass this.
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    
    classifier = WasteClassifier(config_path)
    
    # Read model path and device from config
    import yaml
    try:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
            model_path = cfg.get('model', {}).get('path', 'yolov8n.pt')
            device = cfg.get('inference', {}).get('device', 'cpu')
    except Exception:
        model_path = 'yolov8n.pt'
        device = 'cpu'
        
    detector = GarbageDetector(model_path, device=device)
    visualizer = Visualizer()

    source = args.source
    
    # Route to appropriate processor
    if source.lower() == 'webcam':
        process_video_stream(source, detector, classifier, visualizer)
    elif source.lower().endswith(('.mp4', '.avi', '.mov')):
        process_video_stream(source, detector, classifier, visualizer)
    elif source.lower().endswith(('.jpg', '.jpeg', '.png')):
        process_image(source, detector, classifier, visualizer)
    else:
        print("Unsupported source format.")

if __name__ == "__main__":
    main()
