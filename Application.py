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
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QPoint, QTimer

from Printer_Control_App import oppscan2

from Unwarping_App import unwarpingApp
from Unwarping_App.components.common import Header
from Unwarping_App.components.gcodeObject import gcodes

from Printer_Control_App.core import printer as prt


from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PyQt5.QtMultimedia import QCameraInfo
import sys

printer = prt.console_control()

moving = False
next_height = 0

# function to get time stamp between operations
def addTime():
    gcodes.time_stamps.append(time.time())
    achieved_time = gcodes.time_stamps[-1] - gcodes.time_stamps[-2]
    gcodes.readable_time_stamps.append(gcodes.readable_time_stamps[-1] + achieved_time)

def global_poll():
    global moving, next_height
    # If gcodes are ready
    if len(gcodes.gcode_list) > 0:
        line = gcodes.gcode_list[0]

        # Check if next step is to sample
        if "G4" in line and not moving:
            print("Sampling...")
            line = gcodes.gcode_list.pop(0)
            gcodes.completed_gcodes.append(line)
            addTime()
            
            printer.cmd(line)
        
        # Check if next step is to move to a position
        elif "G0" in line and not moving:
            print("Moving to position: ", line)
            line = gcodes.gcode_list.pop(0)
            gcodes.completed_gcodes.append(line)
            addTime()
            
            # If movement is a height adjustment, grab the value so we can compare if the printer is there
            if "Z" in line:
                match = re.search(r'Z(-?\d+)', line)
                next_height = float(match.group(1))

            # Move to position and set flag as true
            printer.cmd(line)
            moving = True
        
        # Command to set absolute positioning, usually first line of gcode list
        elif "G90" in line:
            line = gcodes.gcode_list.pop(0)
            gcodes.completed_gcodes.append(line)

            addTime()
            printer.cmd(line)

        # Check if printer has made it to the expected height, remove moving flag
        elif printer.pos[2] == next_height:
            moving = False

    # Idle
    elif len(gcodes.gcode_list) <= 0:
        print("running...")

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
        print("attempting connection: ", self.idx)
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
        self.idx = 0 if len(cameras) > 0 else None

    # Start running feed
    def run(self):
        if self.idx is not None:
            print("attempting connection: ", self.idx)
            self.capture = cv2.VideoCapture(self.idx)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.running = True
            self.enable_buttons.emit(True)
            
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
                self.enable_buttons.emit(False)
        else:
            print("No available cameras to connect to.")
    
    # Stop feed
    def stop(self):
        self.running = False
        self.enable_buttons.emit(False)
        self.wait()
        if self.capture:
            self.capture.release()

class App(QWidget):
    def __init__(self):
        super().__init__()
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        self.setWindowTitle("CISC 498 - Automated Mass Spectrometry Sampling")

        screen = QApplication.primaryScreen()
        self.screen_size = screen.size()

        self.camera_feed = CameraThread()
        self.lighting_control = LightingThread()

        # Tabs
        self.stack = QStackedWidget()
        self.stack.addWidget(unwarpingApp.Main(self.camera_feed, self.lighting_control, printer))
        self.stack.addWidget(oppscan2.MyApp(self.camera_feed, printer))

        # Set size
        self.width = int(self.screen_size.width() * 0.75)
        self.height = int(self.screen_size.height() * 0.75)
        self.setFixedSize(self.width, self.height)

        # Header to switch tabs
        self.header = Header(self.stack)

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
        # print(f"Tab changed to index: {index}")  # Debug print
        if index == 0:  # unwarpingApp tab
            new_width = int(self.screen_size.width() * 0.75)
            new_height = int(self.screen_size.height() * 0.75)
            self.setFixedSize(new_width, new_height)
        elif index == 1:  # oppscan2 tab
            self.setFixedSize(1400, 900)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()

    global_timer = QTimer(window)
    global_timer.timeout.connect(global_poll)
    global_timer.start(1000)  # every second?

    sys.exit(app.exec_())