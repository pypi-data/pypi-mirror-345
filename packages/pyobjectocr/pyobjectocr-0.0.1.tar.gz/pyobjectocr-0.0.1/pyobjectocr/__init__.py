from ultralytics import YOLO
import pytesseract
from PIL import Image


model = YOLO("yolov8n.pt")


def process_image(image):
    # Run object detection
    results = model(image)[0]
    img = Image.open(image)

    # Parse detected objects
    detected_objects = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        confidence = float(box.conf[0])
        bbox = box.xyxy[0].tolist() 
        detected_objects.append({
            "class": class_name,
            "confidence": confidence,
            "bbox": bbox
        })

    # OCR text extraction
    text = pytesseract.image_to_string(img)

    return {
        "text": text,
        "detections": detected_objects
    }