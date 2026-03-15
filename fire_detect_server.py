from flask import Flask, request
import torch
import cv2
import numpy as np
from pathlib import Path

# Get the absolute path of the project directory
project_dir = Path(__file__).parent.absolute()
model_path = project_dir / 'yolov5' / 'runs' / 'train' / 'fire_detect_model5' / 'weights' / 'best.pt'

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(model_path), force_reload=True)
model.conf = 0.3  # confidence threshold

app = Flask(__name__)

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files and not request.data:
        return "no image", 400

    try:
        img_bytes = request.data
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        results = model(img)
        detections = results.pred[0]

        labels = results.names
        if len(detections):
            class_ids = detections[:, -1].tolist()
            class_names = [labels[int(cls)] for cls in class_ids]
            print("Detected:", class_names)
            if any(name in ['fire', 'smoke'] for name in class_names):
                return "alert", 200

        return "safe", 200

    except Exception as e:
        print("Error:", e)
        return "error", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
