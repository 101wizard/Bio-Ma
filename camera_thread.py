from PySide6.QtCore import QThread, Signal
import cv2

class CameraThread(QThread):
    frameCaptured = Signal(object)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(1)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frameCaptured.emit(frame)
        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()