import cv2
import time
import collections
from datetime import datetime
from MotionDetection import MotionDetector
from PIL import Image, ImageTk

FRAME_RATE = 30
RECORD_FPS = 30
PRE_RECORD_SECONDS = 10
DEBOUNCE_SECONDS = 5

def get_timestamp():
    return datetime.now().strftime("%B %dth, %Y @ %I:%M:%S %p")

class CameraManager:
    def __init__(self, camera_id, rtsp_url, usb_index, canvas, use_usb_var, debounce_var, recording_var):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.usb_index = usb_index
        self.canvas = canvas
        self.use_usb_var = use_usb_var
        self.debounce_var = debounce_var
        self.recording_var = recording_var

        self.buffer = collections.deque(maxlen=FRAME_RATE * PRE_RECORD_SECONDS)
        self.recording = False
        self.motion_debounce_timer = 0
        self.recorded_frames = []
        self.running = True

        self.cap = None
        self.prev_frame = None
        self.current_source = None
        self.detector = MotionDetector()

    def start(self):
        self.running = True
        self.canvas.after(0, self.update)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def record_video(self, frames):
        height, width, _ = frames[0].shape
        now = datetime.now()
        timestamp = now.strftime("%B %dth @ %I;%M %p")  # Use ; instead of :
        filename = f"camera_{self.camera_id} {timestamp}.avi"

        out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), RECORD_FPS, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()
        print(f"[Camera {self.camera_id}] Saved recording: {filename}")

    def update(self):
        if not self.running:
            return

        source = self.usb_index if self.use_usb_var.get() else self.rtsp_url
        if source != self.current_source:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(source)
            ret, self.prev_frame = self.cap.read()
            if not ret:
                print(f"[Camera {self.camera_id}] Failed to read initial frame.")
                self.prev_frame = None
            self.current_source = source

        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                timestamp = get_timestamp()
                cv2.putText(frame, timestamp, (10, frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

                motion_detected, motion_level = self.detector.detect(self.prev_frame, frame)
                cv2.putText(frame, f"Motion Level: {motion_level}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                self.buffer.append(frame)

                if motion_detected:
                    if not self.recording:
                        print(f"[Camera {self.camera_id}] Motion detected!")
                        self.recording = True
                        self.recorded_frames = list(self.buffer)
                    self.motion_debounce_timer = DEBOUNCE_SECONDS * FRAME_RATE

                if self.recording:
                    self.recorded_frames.append(frame)
                    if not motion_detected:
                        self.motion_debounce_timer -= 1
                        if self.motion_debounce_timer <= 0:
                            self.record_video(self.recorded_frames)
                            self.recording = False
                            self.recorded_frames = []

                self.debounce_var.set(f"Debounce: {self.motion_debounce_timer // FRAME_RATE}")
                self.recording_var.set("● Recording" if self.recording else "● Not Recording")

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(rgb, (560, 340))
                imgtk = ImageTk.PhotoImage(Image.fromarray(img))
                self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
                self.canvas.image = imgtk

                self.prev_frame = frame

        self.canvas.after(int(1000 / FRAME_RATE), self.update)