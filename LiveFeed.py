import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from CameraManager import CameraManager

CAMERA_SOURCES = [
    {"rtsp": "rtsp://user:pass@ip1:port/stream", "usb": 0},
    {"rtsp": "rtsp://user:pass@ip2:port/stream", "usb": 1},
    {"rtsp": "rtsp://user:pass@ip3:port/stream", "usb": 2}
]

CANVAS_WIDTH = 560
CANVAS_HEIGHT = 340

class CameraWidget:
    def __init__(self, root, camera_id, row, column, span=1):
        self.camera_id = camera_id
        self.source = CAMERA_SOURCES[camera_id - 1]
        self.use_usb = tk.BooleanVar(value=False)
        self.debounce_var = tk.StringVar(value="Debounce: 0")
        self.recording_var = tk.StringVar(value="● Not Recording")

        tk.Label(root, text=f"Camera {camera_id}", font=("Arial", 12), fg="white", bg="#1e1e1e").grid(row=row, column=column, columnspan=span)

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#2e2e2e", highlightthickness=1, highlightbackground="#444")
        self.canvas.grid(row=row+1, column=column, columnspan=span, padx=20, pady=10)

        self.set_placeholder()

        tk.Checkbutton(root, text="Use USB", variable=self.use_usb, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").grid(row=row+2, column=column, sticky="w", padx=20)
        tk.Label(root, textvariable=self.debounce_var, font=("Arial", 10), fg="gray", bg="#1e1e1e").grid(row=row+2, column=column, sticky="e", padx=20)
        tk.Label(root, textvariable=self.recording_var, font=("Arial", 10, "bold"), fg="red", bg="#1e1e1e").grid(row=row+3, column=column, columnspan=span)

        self.manager = CameraManager(
            camera_id=camera_id,
            rtsp_url=self.source["rtsp"],
            usb_index=self.source["usb"],
            canvas=self.canvas,
            use_usb_var=self.use_usb,
            debounce_var=self.debounce_var,
            recording_var=self.recording_var
        )
        self.manager.start()

    def set_placeholder(self):
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(50, 50, 50))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except IOError:
            font = ImageFont.load_default()
        txt = "No Feed"
        bbox = draw.textbbox((0, 0), txt, font=font)
        x = (CANVAS_WIDTH - (bbox[2] - bbox[0])) // 2
        y = (CANVAS_HEIGHT - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), txt, fill=(200, 200, 200), font=font)
        self.canvas.image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)

def main():
    root = tk.Tk()
    root.title("Crypt Surveillance")
    root.configure(bg="#1e1e1e")

    # Title label
    tk.Label(root, text="Crypt Surveillance", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").grid(
        row=0, column=0, columnspan=2, pady=(10, 20)
    )

    # Create camera widgets
    widgets = []
    widgets.append(CameraWidget(root, camera_id=1, row=1, column=0))
    widgets.append(CameraWidget(root, camera_id=2, row=1, column=1))
    widgets.append(CameraWidget(root, camera_id=3, row=4, column=0, span=2))

    # Handle window close
    def on_close():
        print("Shutting down...")
        for widget in widgets:
            widget.manager.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# Make sure this runs when the script is executed
if __name__ == "__main__":
    main()