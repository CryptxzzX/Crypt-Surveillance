import cv2
import numpy as np

MOTION_AREA_THRESHOLD = 1500  # Minimum area of movement to count
SMOOTHING_WINDOW = 5

class MotionDetector:
    def __init__(self):
        self.recent_scores = []

    def detect(self, prev_frame, curr_frame):
        diff = cv2.absdiff(prev_frame, curr_frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_score = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > MOTION_AREA_THRESHOLD)

        self.recent_scores.append(motion_score)
        if len(self.recent_scores) > SMOOTHING_WINDOW:
            self.recent_scores.pop(0)
        smoothed_score = int(np.mean(self.recent_scores))

        motion_detected = smoothed_score > 0
        return motion_detected, smoothed_score