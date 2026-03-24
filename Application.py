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

from Unwarping_App.services import sampling_service, device_service

from Printer_Control_App.core import printer as prt
from Printer_Control_App.core import serialcon
from Printer_Control_App.core import conductance 


from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PyQt5.QtMultimedia import QCameraInfo
import sys

printer = prt.console_control()
conduct = serialcon.SerialConnection()

probe = sampling_service.samplingItem

next_height = 0
next_x = 0
next_y = 0
waiting_for_signal = False

state = "idle"
positioning = "absolute"

delta_z = 0

threshold = 99


def global_poll():
    global state, positioning, next_height, next_x, next_y, delta_z, waiting_for_signal

    if len(probe.gcodes) <= 0 or probe.paused:
        pass
        

    else:
        line = probe.gcodes[0]
        sampling_service.addData(printer, conduct)

        # print(line)
        # print(f"moving: {probe.moving}")
        # print(f"state: {state}")

        # print(probe.moving)

        if not probe.moving:
            # Absolute positioning
            if "G90" in line:
                positioning = "absolute"
                print("Set absolute positioning")
                sampling_service.runGCode(printer, conduct)
            
            # Relative positioning
            elif "G91" in line:
                positioning = "relative"
                print("Set relative positioning")
                sampling_service.runGCode(printer, conduct)

            elif "G4" in line:
                print("Waiting...")
                sampling_service.runGCode(printer, conduct)

            # Printer ready for movement
            if state == "idle":
                if "G0" in line or "G1" in line:
                    print(line)
                    # Z position change
                    if "Z" in line:
                        match = re.search(r"^G0 Z(-?\d+(\.\d+)?) F(\d+(\.\d+)?)$", line)

                        # Downward movement
                        if match and probe.mode == "conductive" and positioning == "relative":
                            delta_z = float(match.group(1))
                            next_height = printer.pos[2] + delta_z

                            probe.moving = True
                            waiting_for_signal = True

                        elif match and positioning == "absolute":
                            next_height = float(match.group(1))

                            probe.moving = True
                            sampling_service.runGCode(printer, conduct)


                        # if "Z-" in line:
                        #     match = re.search(r"^G0 Z(-?\d+(\.\d+)?) F(\d+(\.\d+)?)$", line)

                        #     # Conductive mode
                        #     if probe.mode == "conductive" and positioning == "relative" and match:
                        #         next_height = printer.pos[2] + match.group(1)
                            
                        #     # Constant Z and Drag modes
                        #     elif match and (probe.mode == "constant" or probe.mode =="drag"):
                        #         next_height = float(match.group(1))
                        # # Upward movement (always consistent)
                        # else:
                        #     print("else runs")
                        #     match = re.search(r"^G0 Z(\d+(\.\d+)?) F(\d+(\.\d+)?)$", line)
                        #     next_height = float(match.group(1))

                        
                        # print(next_height)


                    # X and Y position change
                    elif "X" in line and "Y" in line:
                        match_x = re.search(r'X(-?\d+(?:\.\d+)?)', line)
                        match_y = re.search(r'Y(-?\d+(?:\.\d+)?)', line)

                        next_x = float(match_x.group(1))
                        next_y = float(match_y.group(1))

                        probe.moving = True
                        sampling_service.runGCode(printer, conduct)
                # probe.gcodes.pop(0)

            # # Downward movement state
            # elif state == "probing":
            #     if probe.moving:
            #         print(probe.mode, conduct.status)
            #         if probe.mode == "conductive" and conduct.status:
            #             conductance_val = device_service.getConductance(conduct)

            #             print(f"val: {conductance_val}")

            #             # Signal detected, stop reading it
            #             if conductance_val >= threshold:
            #                 probe.gcodes.pop(0)

            #             if printer.pos[2] == next_height:
            #                 probe.moving = False
            #                 state = "idle"

                        # if conductance_val < threshold and printer.pos[2] == next_height:
                        #     state = "idle"
                        #     probe.moving = False

                        # elif conductance_val >= threshold:
                        #     probe.gcodes.pop(0)
                        #     state = "idle"
                        #     probe.moving = False
                        
                        # if printer.pos[2] == next_height:

                # else:
                #     if printer.pos[2] == next_height:
                #         state = "idle"
                #         probe.gcodes.pop(0)


        elif probe.moving:
            # Check for movement
            # print(printer.pos[2], next_height)
            # print(printer.pos[2] == round(next_height, 2))
            if probe.mode == "constant":
                if printer.pos[2] == next_height:
                    print("height reached")
                    probe.moving = False
                    state = "idle"


            elif probe.mode == "drag":
                if printer.pos[2] == next_height:
                    print("height reached")
                    probe.moving = False
                    state = "idle"

                if printer.pos[2] == round(next_height, 2) and printer.pos[0] == next_x and printer.pos[1] == next_y:
                    probe.moving = False
                    state = "idle"

                # elif printer.pos[0] == next_x and printer.pos[1] == next_y:
                #     probe.moving = False
                #     state = "idle"
                else:
                    pass

            elif probe.mode == "conductive":
                # print(state)
                # print(printer.pos[2], next_height)
                # if printer.pos[2] == next_height:
                #     probe.moving = False
                #     state = "idle"

                # print(conduct.status)
                if conduct.status:
                    conductance_val = device_service.getConductance(conduct)
                    # print(conductance_val)

                    print(next_x, next_y, next_height)
                    print(printer.pos)

                    if positioning == "relative":
                        if conductance_val >= threshold and waiting_for_signal and printer.pos == [next_x, next_y, round(next_height, 2)]:
                            waiting_for_signal = False
                            probe.moving = False
                            state = "idle"
                            probe.gcodes.pop(0)
                        
                        elif conductance_val < threshold:
                            probe.moving = True
                            next_height = printer.pos[2] + delta_z
                            printer.cmd(line)

                        

                    elif positioning == "absolute":
                        probe.moving = False
                        state = "idle"

                    # if conductance_val >= threshold and waiting_for_signal and printer.pos[2] == next_x and printer.pos[1] == next_y and printer.pos[2] == next_height:
                    #     waiting_for_signal = False
                    #     probe.moving = False
                    #     state = "idle"
                    #     probe.gcodes.pop(0)
                    
                    # elif printer.pos[2] == next_height and conductance_val < threshold and positioning == "relative":
                    #     probe.moving = True
                    #     next_height = printer.pos[2] + delta_z
                    #     # printer.cmd(line)
                    
                    # elif printer.pos[2] == next_height and positioning == "absolute":
                    #     probe.moving = False
                    #     state = "idle"
                    
                    # else:
                    #     printer.cmd(line)
                
                else:
                    print("No condutance detected. Will not perform sampling run.")
                    probe.gcodes = []

                # probe.moving = False
                # state = "idle"
                
                # elif printer.pos[0] == next_x and printer.pos[1] == next_y:
                #     probe.moving = False
                #     state = "idle"
                
                # elif printer.pos[0] == next_x and printer.pos[1] == next_y:
                #     probe.moving = False
                #     state = "idle"
            
            






# def global_poll():
#     global next_height, next_x, next_y, waiting_for_signal,positioning

#     # If there are GCodes available (only when sampling run is started)
#     if len(probe.gcodes) > 0 and not probe.paused:
#         line = probe.gcodes[0]

#         # Check that printer is not moving
#         if not probe.moving:
#             # Sample/Dwell time
#             if "G4" in line:
#                 print("Waiting...")

#             # Absolute positioning
#             elif "G90" in line:
#                 positioning = "absolute"
#                 print("Absolute positioning")

#             # Relative positioning
#             elif "G91" in line:
#                 positioning = "relative"
#                 print("Relative positioning")

#             # XY or Z change
#             elif "G0" in line or "G1" in line:
#                 print(f"Moving to position: {line}")
#                 probe.moving = True

#                 # Height adjustment
#                 if "Z" in line:

#                     # Constant-Z and Drag sampling modes
#                     if probe.mode == "constant" or probe.mode == "drag":
#                         match = re.search(r'Z(-?\d+(?:\.\d+)?)', line)
#                         next_height = float(match.group(1))

#                     # Conductive mode
#                     elif probe.mode == "conductive" and conduct.status:
#                         if waiting_for_signal:
#                             match = re.search(r"^G0 Z-(\d+(\.\d+)?) F(\d+(\.\d+)?)$", line)
                            
#                             if match:
#                                 next_height = printer.pos[2] - float(match.group[1])
#                                 conductance_val = device_service.getConductance(conduct)

#                                 if conductance_val < 99:
#                                     printer.cmd(line)
#                                     probe.moving = True
                                
#                                 elif conductance_val >= 99:
#                                     waiting_for_signal = False
#                                     probe.gcodes.pop(0)

#                             else:
#                                 pass


#                 # (X, Y) adjustment (hold only for drag sampling)
#                 elif "X" in line and "Y" in line and probe.mode == "drag":
#                     match_x = re.search(r'X(-?\d+(?:\.\d+)?)', line)
#                     match_y = re.search(r'Y(-?\d+(?:\.\d+)?)', line)

#                     next_x = float(match_x.group(1))
#                     next_y = float(match_y.group(1))


#             sampling_service.runGCode(printer, conduct)
            
#             # probe.gcodes.pop(0)

#         if probe.mode == "drag" and probe.moving and (printer.pos[0] == next_x) and (printer.pos[1] == next_y):
#             probe.moving = False

#         if positioning == "absolute":
#             if probe.moving and printer.pos[2] == next_height:
#                 probe.moving = False

#         elif positioning == "relative":
#             if probe.moving and printer.pos[2] == next_height:
#                 probe.moving = False

#             elif probe.moving and printer.pos[2] == probe.transitHeight:
#                 probe.moving = False
#                 waiting_for_signal = True
            

#         sampling_service.addData(printer, conduct)

#     # Idle
#     elif len(probe.gcodes) <= 0 or probe.paused:
#         pass



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
        self.stack.addWidget(oppscan2.MyApp(self.camera_feed, printer, conduct))

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