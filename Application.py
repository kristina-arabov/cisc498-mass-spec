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
from Printer_Control_App.core import conductance 


from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PyQt5.QtMultimedia import QCameraInfo
import sys

printer = prt.console_control()
conduct = conductance.ConThread()

probe = sampling_service.samplingItem

next_height = 0

def global_poll():
    global next_height
    # If there are GCodes available (only when sampling run is started)
    if len(probe.gcodes) > 0 and not probe.paused:
        # sampling_service.addData(printer, conduct)
        line = probe.gcodes[0]

        # Check that printer is not moving
        if not probe.moving:
            # Sample/Dwell time
            if "G4" in line:
                print("Waiting...")

            # Absolute positioning
            elif "G90" in line:
                print("Absolute positioning")

            # Relative positioning
            elif "G91" in line:
                print("Relative positioning")

            # XY or Z change
            elif "G0" in line or "G1" in line:
                print(f"Moving to position: {line}")
                probe.moving = True

                # Height adjustment
                if "Z" in line:

                    # Constant-Z and Drag sampling modes
                    if probe.mode == "constant" or probe.mode == "drag":
                        match = re.search(r'Z(-?\d+(?:\.\d+)?)', line)
                        next_height = float(match.group(1))

                    # Conductive mode
                    elif probe.mode == "conductive":
                        pass

            sampling_service.runGCode(printer)

        # # Check if printer has made it to the expected height, remove moving flag
        # elif probe.moving and "M400" in line:
        #     sampling_service.runGCode(printer)
        #     probe.moving = False


        elif probe.moving and printer.pos[2] == next_height:
            probe.moving = False

        sampling_service.addData(printer, conduct)

    # Idle
    elif len(probe.gcodes) <= 0 or probe.paused:
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
    global_timer.start(60)  # every .5 seconds

    sys.exit(app.exec_())