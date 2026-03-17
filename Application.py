import sys
sys.dont_write_bytecode = True

# Add Printer_Control_App/core to path so printrun can be imported
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Printer_Control_App', 'core'))

from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout
import serial
import time
import cv2
import threading
import re
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QPoint, QTimer, QObject

from Printer_Control_App import oppscan2

from Unwarping_App import unwarpingApp
from Unwarping_App.components.common import Header

from Unwarping_App.services import sampling_service

from Printer_Control_App.core import printer as prt


from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PyQt5.QtMultimedia import QCameraInfo
import sys

printer = prt.console_control()

next_height = 0

def global_poll():
    global next_height
    # If gcodes are ready
    if len(sampling_service.samplingItem.gcodes) > 0 and not sampling_service.samplingItem.paused:
        line = sampling_service.samplingItem.gcodes[0]

        # Check if next step is to sample/dwell
        if "G4" in line and not sampling_service.samplingItem.moving:
            print("Waiting...")
            sampling_service.runGCode(printer)

        # Check if next step is to move to a position
        elif "G0" in line and not sampling_service.samplingItem.moving:
            print("Moving to position: ", line)
            
            # Height adjustment
            if "Z" in line:
                # Grab current height to later compare if the printer has reached it (Constant-Z and Drag mode)
                if sampling_service.samplingItem.mode == "constant" or sampling_service.samplingItem.mode == "drag":
                    match = re.search(r'Z(-?\d+(?:\.\d+)?)', line)
                    next_height = float(match.group(1))

                    # Move to position and set moving flag as true
                    sampling_service.runGCode(printer)
                    sampling_service.samplingItem.moving = True

                # Run relative downward movement until printer has detected a conductance value (Conductive mode)
                elif sampling_service.samplingItem.mode == "conductive":
                    pattern = r"^G0 Z-(\d+(\.\d+)?) F(\d+(\.\d+)?)$"
                    print(re.match(pattern, line))
                    if re.match(pattern, line):
                        
                        # TODO change to conductance read
                        for i in range(3):
                            print(line)
                            # printer.cmd(line) 
                            print(i)

                        sampling_service.samplingItem.gcodes.pop(0)
                    else:
                        sampling_service.runGCode(printer)

            else:
                sampling_service.runGCode(printer)
            
        
        # Absolute (G90) or relative (G91) positioning 
        elif "G90" in line or "G91" in line:
            sampling_service.runGCode(printer)

        # Check if printer has made it to the expected height, remove moving flag
        elif printer.pos[2] == next_height:
            sampling_service.samplingItem.moving = False

        sampling_service.addData(printer)

    # Idle
    elif len(sampling_service.samplingItem.gcodes) <= 0 or sampling_service.samplingItem.paused:
        pass



class LightingThread(QThread):
    light_signal = pyqtSignal(str)
    enable_buttons = pyqtSignal(bool)

    def __init__(self, idx='COM3', baudrate=9600):
        super().__init__()
        self.baudrate = baudrate
        self.idx = idx
        self.serial_conn = None
        self.running = False
        
    def run(self):
        print("Attempting lights connection: ", self.idx)
        try:
            self.running = True
            self.serial_conn = serial.Serial(self.idx, self.baudrate, timeout=1)
            self.enable_buttons.emit(True)

            while self.running:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    self.data_received.emit(line)
        except serial.SerialException as e:
            self.running = False
            self.enable_buttons.emit(False)
            print(f"Serial error: {e}")

    # TODO
    # Doesnt entirely work, will make a workaround
    def stop(self):
        self.running = False
        self.enable_buttons.emit(False)

        print("function --->", self.running)

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            time.sleep(0.1)
            self.serial_conn.close()

            self.serial_conn = None
            self.idx = None


# Element to update camera feed 
class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    enable_buttons = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        cameras = QCameraInfo.availableCameras()
        self.running = False
        self.cap = None

        self.idx = None
        self.resolution = None

    # Start running feed
    def run(self):
        if self.idx is not None:
            print("Attempting camera connection: ", self.idx)
            self.capture = cv2.VideoCapture(self.idx)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.running = True

            if self.capture.isOpened():
                while self.running:
                    ret, img = self.capture.read()
                    if ret:
                        self.frame = img
                        self.change_pixmap_signal.emit(img)
                    elif not ret:
                        self.stop()

            else:
                self.running = False
        else:
            print("No available cameras to connect to.")
    
    # Stop feed
    def stop(self):
        self.running = False
        self.wait()
        if self.capture:
            self.capture.release()

# The main application window
class App(QWidget):
    def __init__(self):
        super().__init__()
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        self.setWindowTitle("CISC 498 - Automated Mass Spectrometry Sampling")

        screen = QApplication.primaryScreen()
        self.screen_size = screen.size()
        self.available = screen.availableGeometry()

        self.camera_feed = CameraThread()
        self.lighting_control = LightingThread()

        # Tabs
        self.stack = QStackedWidget()
        self.stack.addWidget(unwarpingApp.Main(self.camera_feed, self.lighting_control, printer))
        self.stack.addWidget(oppscan2.MyApp(self.camera_feed, printer))

        # Set size
        self.width = min(1400, int(self.available.width() * 0.75))
        self.height = min(900, int(self.available.height() * 0.85))

        if self.available.width() < 1400 and self.available.height() < 900:
            self.width = self.available.width() - 50
            self.height = self.available.height() - 50
            
        self.setFixedSize(self.width, self.height)

        # Header to switch tabs
        self.header = Header(self.stack, self.camera_feed, self.lighting_control)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.header)
        layout.addWidget(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.stack.currentChanged.connect(self.on_tab_changed)

        self.resize(self.width, self.height)
        self.stack.setCurrentIndex(0)

    
    # Handle resizing between unwarping and printer control apps
    def on_tab_changed(self, index):
        if index == 0:  # unwarpingApp tab
            width = min(1400, int(self.available.width() * 0.75))
            height = min(900, int(self.available.height() * 0.85))

            if self.available.width() < 1400 and self.available.height() < 900:
                width = self.available.width() - 50
                height = self.available.height() - 50
    
            self.setFixedSize(width, height)
        
        elif index == 1:  # oppscan2 tab
            width = min(1400, self.available.width())
            height = min(900, self.available.height() - 50)

            self.setFixedSize(width, height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()

    global_timer = QTimer(window)
    global_timer.timeout.connect(global_poll)
    global_timer.start(500)  # every .5 seconds

    sys.exit(app.exec_())