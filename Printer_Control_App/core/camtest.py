import sys
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
from camera import CamThread  # Assuming CamThread is in CamThread.py

class CameraApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI components
        self.setWindowTitle("Camera App")
        self.setGeometry(200, 100, 600, 400)

        # QLabel to display the video feed
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setGeometry(50, 50, 500, 300)

        # Start Camera button
        self.start_camera_button = QtWidgets.QPushButton("Start Camera", self)
        self.start_camera_button.setGeometry(50, 360, 150, 30)
        self.start_camera_button.clicked.connect(self.start_camera)

        # Start and stop buttons for recording
        self.start_button = QtWidgets.QPushButton("Start Recording", self)
        self.start_button.setGeometry(210, 360, 150, 30)
        self.start_button.clicked.connect(self.start_recording)

        self.stop_button = QtWidgets.QPushButton("Stop Recording", self)
        self.stop_button.setGeometry(370, 360, 150, 30)
        self.stop_button.clicked.connect(self.stop_recording)

        # Stop Camera button
        self.stop_camera_button = QtWidgets.QPushButton("Stop Camera", self)
        self.stop_camera_button.setGeometry(530, 360, 150, 30)
        self.stop_camera_button.clicked.connect(self.stop_camera)

        # Initialize CamThread
        self.cam_thread = CamThread()
        self.cam_thread.frame_ready.connect(self.update_frame)

    def update_frame(self, frame):
        # Convert the frame to QImage and display it
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(q_img)
        self.video_label.setPixmap(pixmap)

    def start_camera(self):
        self.cam_thread.cam_num = 0  # Set the camera number (0 for default camera)
        self.cam_thread.start()

    def start_recording(self):
        self.cam_thread.start_recording("output.mp4")

    def stop_recording(self):
        
        self.cam_thread.stop_recording()

    def stop_camera(self):
        # Stop the camera thread and release resources
        self.cam_thread.stop()
        self.video_label.clear()  # Clear the video feed display

    def closeEvent(self, event):
        # Stop the camera thread gracefully
        self.cam_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    camera_app = CameraApp()
    camera_app.show()
    sys.exit(app.exec_())
