import streamlit as st
import cv2
import torch
import numpy as np
from pathlib import Path
import tempfile
import os
from PIL import Image
import time
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Fire Detection Dashboard",
    page_icon="🔥",
    layout="wide"
)

# Add YOLOv5 to system path
YOLOV5_PATH = 'yolov5'
if YOLOV5_PATH not in sys.path:
    sys.path.append(YOLOV5_PATH)

# Import YOLOv5 modules
try:
    from models.common import DetectMultiBackend
    from utils.general import check_img_size, non_max_suppression
    from utils.torch_utils import select_device
except ImportError as e:
    st.error(f"Error importing YOLOv5 modules: {e}")
    st.stop()

def check_dependencies():
    try:
        import torch
        import torchvision
        logger.info(f"PyTorch version: {torch.__version__}")
        return True
    except ImportError as e:
        st.error(f"Missing dependency: {str(e)}")
        st.error("Please run: pip install -r requirements.txt")
        return False

@st.cache_resource(show_spinner=False)
def load_model():
    if not check_dependencies():
        return None

    weights = os.path.join(YOLOV5_PATH, 'runs/train/fire_detect_model5/weights/best.pt')
    if not os.path.exists(weights):
        st.error(f"Model weights not found at {weights}")
        st.error("Please ensure the model is trained and saved in the correct location")
        return None

    device = select_device('')
    model = DetectMultiBackend(weights, device=device)
    model.eval()
    logger.info("Model loaded successfully")
    return model

def process_image(image, model, conf_thres=0.25):
    try:
        if isinstance(image, Image.Image):
            image = np.array(image)

        im0 = image.copy()
        h0, w0 = im0.shape[:2]

        img = cv2.resize(im0, (640, 640))
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, CHW
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(model.device)
        img = img.float() / 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        with torch.no_grad():
            pred = model(img)

        pred = non_max_suppression(pred, conf_thres=conf_thres, iou_thres=0.45, max_det=1000)

        for det in pred:
            if det is not None and len(det):
                det = det.cpu().numpy()
                scale_w, scale_h = w0 / 640, h0 / 640
                det[:, [0, 2]] *= scale_w
                det[:, [1, 3]] *= scale_h

                for *xyxy, conf, cls in reversed(det):
                    x1, y1, x2, y2 = map(int, xyxy)
                    label = f'Fire {conf:.2f}'
                    cv2.rectangle(im0, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(im0, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return im0
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        st.error(f"Error processing image: {e}")
        return None

def process_video(video_file, model, conf_thres=0.25):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(video_file.read())
            video_path = tmp_file.name

        cap = cv2.VideoCapture(video_path)
        frames = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame = process_image(frame, model, conf_thres)
            if processed_frame is not None:
                frames.append(processed_frame)

        cap.release()
        os.unlink(video_path)
        return frames
    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        st.error(f"Error processing video: {e}")
        return []

def main():
    st.title("🔥 Fire Detection Dashboard")

    # Initialize session state for stream control
    if 'stream_active' not in st.session_state:
        st.session_state.stream_active = False

    # Sidebar settings
    st.sidebar.header("Settings")
    conf_thres = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)

    # Load model
    with st.spinner("Loading model..."):
        model = load_model()
        if model is None:
            st.error("Failed to load model. Please check the error messages above.")
            return

    st.header("ESP32-CAM Live Feed")
    esp32_ip = st.text_input("Enter ESP32-CAM IP (e.g. http://192.168.0.100:81/stream)",
                            "http://192.168.0.100:81/stream")

    col1, col2 = st.columns(2)
    
    if not st.session_state.stream_active:
        if col1.button("Start ESP32-CAM Stream", key="start_esp32"):
            st.session_state.stream_active = True
            st.experimental_rerun()
    else:
        if col2.button("Stop ESP32-CAM Stream", key="stop_esp32"):
            st.session_state.stream_active = False
            st.experimental_rerun()

    if st.session_state.stream_active:
        try:
            # Add timeout to VideoCapture
            cap = cv2.VideoCapture(esp32_ip, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not cap.isOpened():
                st.error("Unable to connect to ESP32-CAM stream. Please check:")
                st.error("1. ESP32-CAM is powered on")
                st.error("2. ESP32-CAM is connected to WiFi")
                st.error("3. IP address is correct")
                st.error("4. Stream URL is correct (should end with /stream)")
                st.session_state.stream_active = False
                st.experimental_rerun()
                return

            stframe = st.empty()
            retry_count = 0
            max_retries = 3

            while cap.isOpened() and st.session_state.stream_active:
                ret, frame = cap.read()
                if not ret:
                    retry_count += 1
                    if retry_count >= max_retries:
                        st.error("Lost connection to ESP32-CAM. Please check the connection and try again.")
                        st.session_state.stream_active = False
                        st.experimental_rerun()
                        break
                    time.sleep(1)
                    continue

                processed_frame = process_image(frame, model, conf_thres)
                if processed_frame is not None:
                    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    stframe.image(processed_frame, channels="RGB")

                time.sleep(0.05)

            cap.release()
        except Exception as e:
            logger.error(f"ESP32 stream error: {e}", exc_info=True)
            st.error(f"Stream error: {e}")
            st.error("Please check if the ESP32-CAM is running and the IP address is correct")
            st.session_state.stream_active = False
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("Built with Streamlit and YOLOv5")

if __name__ == "__main__":
    main()
