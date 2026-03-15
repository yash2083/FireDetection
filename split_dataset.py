import os
import shutil
from pathlib import Path
import random
import xml.etree.ElementTree as ET

def convert_xml_to_yolo(xml_file, img_width, img_height):
    """Convert XML annotation to YOLO format"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    yolo_annotations = []
    
    for obj in root.findall('object'):
        # Get class name
        class_name = obj.find('name').text.lower()
        # Map class name to index (0 for fire, 1 for smoke)
        class_idx = 0 if 'fire' in class_name else 1
        
        # Get bounding box
        bbox = obj.find('bndbox')
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)
        
        # Convert to YOLO format (x_center, y_center, width, height)
        x_center = (xmin + xmax) / (2 * img_width)
        y_center = (ymin + ymax) / (2 * img_height)
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height
        
        yolo_annotations.append(f"{class_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    return yolo_annotations

def split_dataset(train_ratio=0.8):
    # Set correct image and annotation paths
    base_path = Path('archive(16)')
    image_path = base_path / 'Datacluster Fire and Smoke Sample' / 'Datacluster Fire and Smoke Sample'
    annotations_path = base_path / 'Annotations' / 'Annotations'

    # Print debug info
    print(f"Looking for images in: {image_path}")
    print(f"Looking for annotations in: {annotations_path}")

    # Verify paths exist
    if not image_path.exists():
        print(f"Error: Image path does not exist: {image_path}")
        print("Current directory contents:")
        for item in Path('.').iterdir():
            print(f"- {item}")
        return

    if not annotations_path.exists():
        print(f"Error: Annotations path does not exist: {annotations_path}")
        return

    # Create dataset directory structure
    dataset_path = Path('dataset')
    train_path = dataset_path / 'images' / 'train'
    val_path = dataset_path / 'images' / 'val'
    for path in [train_path, val_path]:
        path.mkdir(parents=True, exist_ok=True)

    # Get all image files
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        image_files.extend(list(image_path.glob(f'*{ext}')))

    if not image_files:
        print(f"No image files found in {image_path}")
        print("Contents:")
        for item in image_path.iterdir():
            print(f"- {item}")
        return

    print(f"Found {len(image_files)} images. Sample:")
    for img in image_files[:5]:
        print(f"- {img.name}")

    # Shuffle and split
    random.shuffle(image_files)
    split_idx = int(len(image_files) * train_ratio)
    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]
    print(f"Training set size: {len(train_files)}")
    print(f"Validation set size: {len(val_files)}")

    # Copy and convert
    for img_files, target_path in [(train_files, train_path), (val_files, val_path)]:
        for img_file in img_files:
            shutil.copy2(img_file, target_path / img_file.name)
            xml_file = annotations_path / f"{img_file.stem}.xml"
            if xml_file.exists():
                import cv2
                img = cv2.imread(str(img_file))
                img_height, img_width = img.shape[:2]
                yolo_annotations = convert_xml_to_yolo(xml_file, img_width, img_height)
                yolo_file = target_path / f"{img_file.stem}.txt"
                with open(yolo_file, 'w') as f:
                    f.write('\n'.join(yolo_annotations))
            else:
                print(f"Warning: No annotation found for {img_file.name}")

    print("\nDataset split complete!")
    print(f"Training images and annotations copied to: {train_path}")
    print(f"Validation images and annotations copied to: {val_path}")

    # Create data.yaml file
    yaml_content = f"""train: {train_path}\nval: {val_path}\n\nnc: 2\nnames: ['fire', 'smoke']\n"""
    with open('data.yaml', 'w') as f:
        f.write(yaml_content)
    print("\nCreated data.yaml file with dataset configuration")

if __name__ == "__main__":
    split_dataset() 