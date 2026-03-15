import os
import sys
import cv2
import torch
from pathlib import Path

def setup_yolo():
    """Setup YOLOv5 environment"""
    if not os.path.exists('yolov5'):
        print("YOLOv5 not found. Please run setup_yolo.py first.")
        sys.exit(1)
    
    # Add YOLOv5 to path
    sys.path.append('yolov5')
    
    # Import YOLOv5
    try:
        from yolov5 import detect
        return detect
    except ImportError:
        print("Error importing YOLOv5. Please ensure it's properly installed.")
        sys.exit(1)

def run_detection(source, weights='runs/train/fire_detect_model/weights/best.pt', conf_thres=0.25):
    """
    Run fire detection on images or video
    
    Args:
        source: Path to image, video, or directory
        weights: Path to model weights
        conf_thres: Confidence threshold
    """
    detect = setup_yolo()
    
    # Check if weights exist
    if not os.path.exists(weights):
        print(f"Error: Weights file not found at {weights}")
        print("Please ensure training completed successfully.")
        sys.exit(1)
    
    # Run detection
    detect.run(
        weights=weights,
        source=source,
        conf_thres=conf_thres,
        save_txt=True,
        save_conf=True,
        project='runs/detect',
        name='fire_detection'
    )

def main():
    # Get source from command line or use default
    source = sys.argv[1] if len(sys.argv) > 1 else 'test_images'
    
    # Create test_images directory if it doesn't exist
    if source == 'test_images' and not os.path.exists(source):
        os.makedirs(source)
        print(f"Created {source} directory. Please add test images there.")
        return
    
    # Run detection
    print(f"Running fire detection on {source}")
    run_detection(source)
    
    # Print results location
    results_dir = Path('runs/detect/fire_detection')
    if results_dir.exists():
        print(f"\nResults saved to {results_dir}")
        print("You can find:")
        print("- Detected images in the 'results_dir'")
        print("- Detection coordinates in 'labels' folder")
        print("- Confidence scores in the detection results")

if __name__ == "__main__":
    main()
