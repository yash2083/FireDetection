# 🔥 Fire Detection System using YOLOv5 & ESP32-CAM

An edge-AI powered real-time fire and smoke detection system. This project harnesses the power of YOLOv5 for accurate object detection and integrates it with an ESP32-CAM module to provide real-time monitoring through a Streamlit Dashboard and a Flask REST API.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![YOLOv5](https://img.shields.io/badge/YOLOv5-Vision-brightgreen)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32--CAM-Hardware-orange)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📖 Table of Contents
- [Features](#-features)
- [Architecture Setup](#-architecture-setup)
- [Installation](#-installation)
- [Usage](#-usage)
  - [1. Streamlit Dashboard](#1-streamlit-dashboard)
  - [2. Flask Detection API](#2-flask-detection-api)
  - [3. Standalone Detection](#3-standalone-detection)
- [Model Training](#-model-training)
- [ESP32-CAM Setup](#-esp32-cam-setup)
- [License](#-license)

---

## ✨ Features

- **Real-Time Detection:** Run inference locally or via video stream utilizing YOLOv5.
- **ESP32-CAM Integration:** Seamlessly connect ESP32-CAM via HTTP stream to monitor areas remotely.
- **Interactive Dashboard:** A beautiful Streamlit dashboard to manage streams and adjust confidence thresholds on the fly.
- **REST API:** A Flask backend (`/detect`) that processes image bytes and immediately returns alerts (`alert` or `safe`).
- **Custom Dataset Training:** Scripts included to manage, split, and train YOLOv5 with your own fire/smoke datasets.
- **Edge Deployment:** Export models to TFLite for resource-constrained environments.

---

## 🏗 Architecture Setup

1. **Camera Node:** ESP32-CAM captures video and streams it over HTTP.
2. **Server / Dashboard:** A Python Server running `app.py` (Streamlit) or `fire_detect_server.py` (Flask) processes incoming frames.
3. **AI Engine:** YOLOv5 processes the frames and identifies coordinates and confidence levels for "Fire" or "Smoke".
4. **Action:** Annotations are drawn on the Streamlit dashboard, or alerts are sent as HTTP responses via Flask.

---

## 🛠 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yash2083/FireDetection.git
cd FireDetection
```

### 2. Set up Python Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup YOLOv5
Run the setup script to clone YOLOv5 and install its specialized requirements:
```bash
python setup_yolo.py
```

---

## 🚀 Usage

### 1. Streamlit Dashboard
The Streamlit dashboard allows you to connect to the ESP32-CAM live stream and adjust YOLOv5 detection confidence.

```bash
streamlit run app.py
```
- A web browser will open automatically.
- Enter your ESP32-CAM Stream IP (e.g., `http://192.168.0.100:81/stream`).
- Adjust the confidence threshold on the left sidebar.

### 2. Flask Detection API
To run a headless server that accepts images via POST requests and returns detection statuses:

```bash
python fire_detect_server.py
```
**Endpoint:** `POST /detect`
- Receives raw image bytes.
- Returns `alert` (if fire/smoke detected), `safe`, or `error` with corresponding HTTP status codes.

### 3. Standalone Detection
To run fire detection on a specific image, video, or directory using the local script:

```bash
python detect_fire.py path/to/your/image_or_video.mp4
```

---

## 🧠 Model Training

Want to train the model on your own dataset?
1. Place your data in the `dataset` folder (see `data.yaml`).
2. Run data preparation:
    ```bash
    python organize_dataset.py
    python split_dataset.py
    ```
3. Start training:
    ```bash
    python train_fire_yolo.py
    ```
4. Export the resulting model to TFLite (Optional):
    ```bash
    python export_tflite.py
    ```

---

## 📷 ESP32-CAM Setup

1. Open the `PlatformIO` project contained in this repository.
2. The `platformio.ini` is pre-configured for the `esp32cam` board.
3. Update `camera_web_server.cpp` with your WiFi credentials (`ssid` and `password`).
4. Build and upload to the ESP32-CAM using PlatformIO.
5. Open the Serial Monitor at `115200` baud rate to retrieve the IP address.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
