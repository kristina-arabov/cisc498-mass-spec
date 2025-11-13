import cv2
from PyQt5 import QtCore, QtWidgets
import os
import time

class CamThread(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(object)
    print('cam')
    def __init__(self, parent=None):
        super(CamThread, self).__init__(parent)
        self.running = False
        self.recording = False
        self.pause = False
        self.frame = None
        self.out = None
        self.cam_num = 0
        self.fps = 30
        
    def run(self):
        # Initialize the camera capture
        self.cap = cv2.VideoCapture(int(self.cam_num)-1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 219)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame. Retrying...")
                continue  # Skip this iteration if the frame is not captured successfully
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame = frame  
            self.frame_ready.emit(frame)  
            
            if self.recording and self.out and not self.pause:
                self.out.write(frame)  # Write the frame to video file

            QtCore.QThread.msleep(int(1000 / self.fps))  

    # def start_recording(self, output_file):
    #     folder = 'Video'
    #     file_path = os.path.join(folder, str(time.time()) + '.mp4')
    #     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #     self.out = cv2.VideoWriter(file_path, fourcc, self.fps, (500, 219))
    #     self.recording = True
    #     print(f"Recording started: {file_path}")
        
        
    def start_recording(self):
        folder = 'video'
        if not os.path.exists(folder):
            os.makedirs(folder)
            print("video folder created")
        file_path = os.path.join(folder, str(time.time()) + '.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'MP4A')
        self.out = cv2.VideoWriter(file_path, fourcc, self.fps, (int(self.cap.get(3)),int(self.cap.get(4))))
        self.recording = True
        print(f"Recording started: {file_path}")
    
        

    def stop_recording(self):
        self.recording = False
        if self.out:
            self.out.release()
            self.out = None
        print("Recording stopped")
    def stop(self):
        self.running = False
        if self.out:
            self.out.release()
        self.cap.release()
        self.quit()
        self.wait()
    def take_photo(self):
        folder = 'Images'
        
        file_path = os.path.join(folder, str(time.time()) + '.jpg')
        cv2.imwrite(file_path, self.frame)
        print("Photo saved")
        
    def pause_recording(self, bool):
        if bool == True:
            
            self.pause = bool
            print("Recording paused")
        else:
            self.pause = bool
            print("Recording resumed")

   
