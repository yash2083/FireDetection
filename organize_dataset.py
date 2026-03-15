import os
import shutil
from pathlib import Path

def organize_dataset():
    # Create labels directories
    os.makedirs('dataset/labels/train', exist_ok=True)
    os.makedirs('dataset/labels/val', exist_ok=True)
    
    # Move label files from train directory
    train_dir = Path('dataset/images/train')
    train_labels_dir = Path('dataset/labels/train')
    
    for file in train_dir.glob('*.txt'):
        shutil.move(str(file), str(train_labels_dir / file.name))
        print(f"Moved {file.name} to labels/train")
    
    # Move label files from val directory
    val_dir = Path('dataset/images/val')
    val_labels_dir = Path('dataset/labels/val')
    
    for file in val_dir.glob('*.txt'):
        shutil.move(str(file), str(val_labels_dir / file.name))
        print(f"Moved {file.name} to labels/val")
    
    print("\nDataset organization complete!")
    print("Directory structure:")
    print("dataset/")
    print("├── images/")
    print("│   ├── train/")
    print("│   │   └── *.jpg")
    print("│   └── val/")
    print("│       └── *.jpg")
    print("└── labels/")
    print("    ├── train/")
    print("    │   └── *.txt")
    print("    └── val/")
    print("        └── *.txt")

if __name__ == "__main__":
    organize_dataset() 