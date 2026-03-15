import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the absolute path of the project directory
    project_dir = Path(__file__).parent.absolute()
    
    # Check if YOLOv5 is installed
    yolov5_dir = project_dir / 'yolov5'
    if not yolov5_dir.exists():
        print("Error: YOLOv5 not found!")
        print("Please run setup_yolo.py first to install YOLOv5")
        sys.exit(1)
    
    # Check if dataset exists
    dataset_dir = project_dir / 'dataset'
    if not dataset_dir.exists():
        print("Error: Dataset not found!")
        print("Please run split_dataset.py first to prepare your dataset")
        sys.exit(1)
    
    # Check if data.yaml exists
    data_yaml = project_dir / 'data.yaml'
    if not data_yaml.exists():
        print("Error: data.yaml not found!")
        print("Please run split_dataset.py first to prepare your dataset")
        sys.exit(1)
    
    # Start training
    print("Starting training...")
    os.chdir(yolov5_dir)
    
    try:
        # Use relative path for data.yaml since we're in the yolov5 directory
        subprocess.run([
            sys.executable, 'train.py',
            '--data', '../data.yaml',
            '--img', '416',
            '--batch', '16',
            '--epochs', '50',
            '--weights', 'yolov5n.pt',
            '--name', 'fire_detect_model'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during training: {e}")
        print("\nPlease try running these commands manually:")
        print(f"cd {yolov5_dir}")
        print("python train.py --data ../data.yaml --img 416 --batch 16 --epochs 50 --weights yolov5n.pt --name fire_detect_model")
        sys.exit(1)

if __name__ == "__main__":
    main()
