import cv2

class CameraHandler:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        """Initialize and start the camera capture"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")
        return self.cap.isOpened()

    def get_frame(self):
        """Capture a single frame from the camera"""
        if not self.cap or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        """Release the camera resource"""
        if self.cap:
            self.cap.release()
            self.cap = None