import os
import sys
import urllib.request
import zipfile
import shutil
import time
import subprocess
from pathlib import Path

def download_file(url, filename):
    """Download a file with progress bar"""
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        if not os.path.exists(filename):
            raise Exception(f"Downloaded file {filename} not found")
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

def force_remove_directory(path):
    """Force remove a directory and its contents"""
    if os.path.exists(path):
        try:
            # Try to remove read-only attributes
            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    os.chmod(os.path.join(root, dir), 0o777)
                for file in files:
                    os.chmod(os.path.join(root, file), 0o777)
            # Remove the directory
            shutil.rmtree(path, ignore_errors=True)
            time.sleep(1)  # Wait a bit
        except Exception as e:
            print(f"Warning: Could not remove {path}: {e}")
            return False
    return True

def verify_yolo_installation():
    """Verify that YOLOv5 is properly installed"""
    required_files = ['train.py', 'detect.py', 'models', 'utils']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join('yolov5', file)):
            missing_files.append(file)
    
    if missing_files:
        print("Error: YOLOv5 installation is incomplete. Missing files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    return True

def setup_yolo():
    print("Starting YOLOv5 setup...")
    
    # Force cleanup of existing directories
    print("Cleaning up existing directories...")
    force_remove_directory('yolov5')
    force_remove_directory('yolov5-master')
    force_remove_directory('yolov5.zip')
    
    # Create a temporary directory for extraction
    temp_dir = 'temp_yolo_extract'
    force_remove_directory(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download YOLOv5
    yolo_zip = 'yolov5.zip'
    download_file('https://github.com/ultralytics/yolov5/archive/refs/heads/master.zip', yolo_zip)
    
    # Extract YOLOv5 to temporary directory
    print("Extracting YOLOv5...")
    try:
        with zipfile.ZipFile(yolo_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        print(f"Error extracting YOLOv5: {e}")
        force_remove_directory(temp_dir)
        sys.exit(1)
    
    # Wait a moment to ensure extraction is complete
    time.sleep(2)
    
    # Move contents from temporary directory
    print("Setting up YOLOv5 directory...")
    try:
        extracted_dir = os.path.join(temp_dir, 'yolov5-master')
        if os.path.exists(extracted_dir):
            # Create fresh yolov5 directory
            os.makedirs('yolov5', exist_ok=True)
            # Copy contents
            for item in os.listdir(extracted_dir):
                src = os.path.join(extracted_dir, item)
                dst = os.path.join('yolov5', item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        else:
            print("Error: Could not find extracted YOLOv5 directory")
            force_remove_directory(temp_dir)
            sys.exit(1)
    except Exception as e:
        print(f"Error setting up YOLOv5 directory: {e}")
        force_remove_directory(temp_dir)
        sys.exit(1)
    
    # Clean up
    force_remove_directory(temp_dir)
    force_remove_directory(yolo_zip)
    
    # Verify installation
    if not verify_yolo_installation():
        print("Error: YOLOv5 installation verification failed")
        sys.exit(1)
    
    # Install requirements
    print("Installing requirements...")
    os.chdir('yolov5')
    
    # Create requirements.txt if it doesn't exist
    requirements = """torch>=1.7.0
torchvision>=0.8.1
opencv-python>=4.1.2
numpy>=1.18.5
pandas>=1.1.4
seaborn>=0.11.0
pyyaml>=5.3.1
tqdm>=4.41.0
matplotlib>=3.2.2
seaborn>=0.11.0
tensorboard>=2.4.1
ipython
psutil
thop"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    # Install requirements
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        print("Trying to install key packages manually...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                'torch', 'torchvision', 'opencv-python', 'numpy',
                'pandas', 'pyyaml', 'tqdm', 'matplotlib', 'seaborn'
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing key packages: {e}")
            sys.exit(1)
    
    # Go back to original directory
    os.chdir('..')
    
    # Final verification
    if verify_yolo_installation():
        print("\nYOLOv5 setup complete!")
        print("You can now run the training script.")
    else:
        print("\nError: YOLOv5 setup failed. Please try running the script again.")
        sys.exit(1)

if __name__ == "__main__":
    setup_yolo() 