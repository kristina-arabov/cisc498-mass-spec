# capture_stdout.py
import sys
import io
from PyQt5 import QtCore
import time

class CaptureStdout(QtCore.QThread):
    new_output_signal = QtCore.pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.captured_stdout = io.StringIO()
        self.original_stdout = sys.stdout
        self.running = False

    def __enter__(self):
        sys.stdout = self.captured_stdout
        return self.captured_stdout

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.original_stdout

    def run(self):
        self.running = True
        sys.stdout = self.captured_stdout
        while self.running:
            time.sleep(1)
            self.check_output()

    def check_output(self):
        self.captured_stdout.seek(0, io.SEEK_END)  # Move to the end of the buffer
        if self.captured_stdout.tell() > 0:
            self.captured_stdout.seek(0)  # Move to the start
            output = self.captured_stdout.read()
            self.new_output_signal.emit(output)
            self.captured_stdout.seek(0)
            self.captured_stdout.truncate(0)  # Clear the buffer

    def stop(self):
        self.running = False
        sys.stdout = self.original_stdout
