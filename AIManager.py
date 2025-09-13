# AIManager.py
from ultralytics import YOLO

class AIManager:
    def __init__(self, model_path="YOUR MODEL HERE.pt", confidence_threshold=0.5): # Replace with your model path
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect_objects(self, frame):
        results = self.model.predict(source=frame, verbose=False)
        detections = results[0]

        # Basic Hand Detection, use a general object detection model for more classes
        hands = []
        if detections.boxes is not None:
            for i, box in enumerate(detections.boxes.xyxy):
                conf = detections.boxes.conf[i].item()
                if conf >= self.confidence_threshold:
                    hands.append({
                        "box": box.cpu().numpy()  # [xmin, ymin, xmax, ymax]
                    })

        return hands