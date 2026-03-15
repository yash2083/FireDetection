import torch

# Load PyTorch model
model = torch.load('yolov5/runs/train/fire_detect_model/weights/best.pt')['model'].float()
model.eval()

# Export to TorchScript
ts = torch.jit.script(model)
ts.save("fire_detector.torchscript.pt")

# Export to ONNX
dummy_input = torch.zeros((1, 3, 416, 416))
torch.onnx.export(model, dummy_input, "fire_detector.onnx", verbose=True)

print("Exported to TorchScript and ONNX.")
