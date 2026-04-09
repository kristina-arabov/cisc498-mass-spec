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

positioning = "absolute"

delta_z = 0



def global_poll():
    global positioning, next_height, next_x, next_y, delta_z, waiting_for_signal

    if len(probe.gcodes) <= 0 or probe.paused:
        pass
        

    else:
        line = probe.gcodes[0]
        sampling_service.addData(printer, conduct)

        # Probe is ready to move
        if not probe.moving:
            # Absolute positioning
            if "G90" in line:
                positioning = "absolute"
                print("ABSOLUTE POSITIONING")
                sampling_service.runGCode(printer, conduct)
            
            # Relative positioning
            elif "G91" in line:
                positioning = "relative"
                print("RELATIVE POSITIONING")
                sampling_service.runGCode(printer, conduct)

            elif "G4" in line:
                print("Waiting...")
                sampling_service.runGCode(printer, conduct)

            # Printer ready for movement
            elif "G0" in line or "G1" in line:
                print(f"Moving to position: {line}")
                
                # Z position change
                if "Z" in line:
                    match = re.search(r"^G0 Z(-?\d+(\.\d+)?) F(\d+(\.\d+)?)$", line)

                    # Downward movement
                    if match and (probe.mode == "conductive" or probe.ref_mode == "conductive") and positioning == "relative":
                        delta_z = float(match.group(1))
                        next_height = printer.pos[2] + delta_z

                        probe.moving = True
                        waiting_for_signal = True
                        printer.cmd(line) # send inital step

                    elif match and positioning == "absolute":
                        next_height = float(match.group(1))

                        probe.moving = True
                        sampling_service.runGCode(printer, conduct)

                # X and Y position change
                elif "X" in line and "Y" in line:
                    match_x = re.search(r'X(-?\d+(?:\.\d+)?)', line)
                    match_y = re.search(r'Y(-?\d+(?:\.\d+)?)', line)

                    next_x = float(match_x.group(1))
                    next_y = float(match_y.group(1))

                    probe.moving = True
                    sampling_service.runGCode(printer, conduct)

        # Probe is moving
        elif probe.moving:

            # Reference point will always be sampled first, check if it has been probed
            if not probe.ref_point_probed:
                pos = printer.pos

                # Constant-Z mode for reference point
                if probe.ref_mode == "constant" and pos[2] == next_height:
                    probe.moving = False
                
                    if (pos[0], pos[1]) == (round(probe.dot[0], 2), round(probe.dot[1], 2)):
                        probe.ref_point_probed = True # Reference point has been probed


                # Conductive mode for reference point
                elif probe.ref_mode == "conductive":
                    if conduct.status:
                        conductance_val = device_service.getConductance(conduct)

                        # Relative positioning handling
                        if positioning == "relative":

                            # Conductance threshold reached and software was waiting for signal... helps to not affect other GCodes
                            if conductance_val >= printer.con_threshold and waiting_for_signal and (pos[0], pos[1]) == (round(probe.dot[0], 2), round(probe.dot[1], 2)):
                                waiting_for_signal = False
                                probe.moving = False
                                probe.ref_point_probed = True # Reference point has been probed

                                probe.gcodes.pop(0)
                            
                            # If conductance threshold has not been reached, keep moving down
                            elif conductance_val < printer.con_threshold:
                                probe.moving = True
                                next_height = printer.pos[2] + delta_z

                                printer.cmd(line)

                        # Absolute positioning handling
                        elif positioning == "absolute":
                            probe.moving = False

                    # If no conductance connected, do not perform sampling!!!
                    else:
                        print("No condutance detected. Will not perform sampling run.")
                        probe.gcodes = []
            


            # Checks for Constant-Z sampling mode
            elif probe.mode == "constant":
                if printer.pos[2] == next_height:
                    probe.moving = False


            # Checks for Drag sampling mode
            elif probe.mode == "drag":
                
                if printer.pos[2] == next_height:
                    probe.moving = False

                if printer.pos[2] == round(next_height, 2) and printer.pos[0] == next_x and printer.pos[1] == next_y:
                    probe.moving = False

                else:
                    pass


            # Checks for Conductive mode
            elif probe.mode == "conductive":
                if conduct.status:
                    conductance_val = device_service.getConductance(conduct)

                    # Relative positioning handling
                    if positioning == "relative":

                        # Conductance threshold reached and software was waiting for signal... helps to not affect other GCodes
                        if conductance_val >= printer.con_threshold and waiting_for_signal and printer.pos[0] == next_x and printer.pos[1] == next_y:
                            waiting_for_signal = False
                            probe.moving = False

                            probe.gcodes.pop(0)
                        
                        # If conductance threshold has not been reached, keep moving down
                        elif conductance_val < printer.con_threshold:
                            probe.moving = True
                            next_height = printer.pos[2] + delta_z

                            printer.cmd(line)

                    # Absolute positioning handling
                    elif positioning == "absolute":
                        probe.moving = False

                # If no conductance connected, do not perform sampling!!!
                else:
                    print("No conductance detected. Will not perform sampling run.")
                    probe.gcodes = []



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


# Backends tried in order. CAP_DSHOW bypasses the MSMF stack and is faster/
# more reliable for most USB webcams on Windows.
_CAMERA_BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

# Frames discarded after open to flush the driver buffer and let AE/AWB settle.
_CAMERA_WARMUP_FRAMES = 5

# Consecutive failed reads before the thread treats the camera as lost.
_MAX_READ_FAILURES = 10


class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    enable_buttons = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = False
        self.capture = None   # set before run() so device_service can call isOpened()
        self.frame   = None   # set before run() so workers never get AttributeError
        self.idx        = None
        self.resolution = None

    # ── Connection ────────────────────────────────────────────────────────────

    def run(self):
        if self.idx is None:
            print("CameraThread: no camera index set.")
            return

        w, h = self.resolution if self.resolution else (1280, 720)
        print(f"Attempting camera connection: {self.idx}  ({w}×{h})")

        self.capture = self._open_capture(self.idx, w, h)

        if self.capture is None:
            print(f"CameraThread: could not open camera {self.idx} on any backend.")
            self.running = False
            self.enable_buttons.emit(False)
            return

        self.running = True
        self.enable_buttons.emit(True)

        consecutive_failures = 0
        while self.running:
            ret, img = self.capture.read()
            if ret:
                consecutive_failures = 0
                self.frame = img
                self.change_pixmap_signal.emit(img)
            else:
                consecutive_failures += 1
                if consecutive_failures >= _MAX_READ_FAILURES:
                    print(f"CameraThread: camera {self.idx} stopped responding — disconnecting.")
                    break

        self.running = False
        self.capture.release()
        self.capture = None

    def _open_capture(self, idx, w, h):
        """
        Try each backend in _CAMERA_BACKENDS until one produces a valid frame.
        Returns an open VideoCapture, or None if all backends fail.
        """
        for backend in _CAMERA_BACKENDS:
            try:
                cap = cv2.VideoCapture(idx, backend)
            except Exception as e:
                print(f"  Backend {backend}: exception during open — {e}")
                continue

            if not cap.isOpened():
                cap.release()
                continue

            # Set resolution before reading so the driver negotiates the right mode.
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

            # Warmup: discard frames to flush stale buffer data and let
            # auto-exposure / auto-white-balance converge.
            for _ in range(_CAMERA_WARMUP_FRAMES):
                cap.read()

            # Confirm we can actually get a frame on this backend.
            ret, _ = cap.read()
            if ret:
                print(f"  Camera {idx} opened with backend {backend}.")
                return cap

            cap.release()

        return None

    # ── Disconnection ─────────────────────────────────────────────────────────

    def stop(self):
        self.running = False
        # Calling wait() from within the thread itself deadlocks — Qt warns about
        # this and the thread never exits.  Only block when called externally.
        if QThread.currentThread() is not self:
            self.wait()
        if self.capture:
            self.capture.release()
            self.capture = None

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
    global_timer.start(100)  # every .5 seconds

    sys.exit(app.exec_())