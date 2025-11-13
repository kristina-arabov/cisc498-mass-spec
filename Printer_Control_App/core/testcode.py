import subprocess
import time
import re
import os  # to check the OS name
from PyQt5 import QtCore, QtGui, QtWidgets
import queue as Queue
import select

class console_control(QtCore.QThread):
    def __init__(self, parent=None):
        super(console_control, self).__init__(parent)
        self.flag = True
        self.prtconnect = False  # port connection
        self.queue = Queue.Queue()  # output queue
        self.posqueue = Queue.Queue()  # position queue
        self.pos = [0, 0, 0]  # position
        self.outputarr = []  # output array
        self.homed = False  # home status
        self.moving = False  # moving status
        self.checkmovequeue = Queue.Queue()  # check move queue
        self.gcodeidx = 0  # gcode index
        self.line = ""  # Initialize line to an empty string
        self.cond = None
        self.con_threshold = 100  # Threshold for conductive touch detection
        self.batch = False  # batch status

    def run(self):
        self.flag = True
        if os.name == 'nt':  # Windows
            self.sc_path = r'cmd.exe --cli --disable_readline'
            self.console = subprocess.Popen(self.sc_path,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)
        else:  # added for mac compatibility
            self.sc_path = ['/bin/bash']
            self.console = subprocess.Popen(self.sc_path,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)
        print('start console thread')

        while self.flag:
            self.readloop()
            self.displayout()

            if 'ok T:' in self.line:  # after G28
                self.homed = True

            if not self.prtconnect:
                if 'Printer is now online' in self.line:
                    print('printer connected')
                    self.prtconnect = True
                    self.cmd("M114")  # maybe remove this
            time.sleep(0.01)

    def readloop(self):
        if self.queue.qsize() < 2:
            rlist, _, _ = select.select([self.console.stdout], [], [], 0.01)
            if rlist:
                self.line = self.console.stdout.readline().strip()
                self.queue.put(self.line)
        else:
            print('sleep 1')
            time.sleep(1)

    def displayout(self):
        if not self.queue.empty():
            line = self.queue.get()
            self.line = line
        else:
            print('sleep 2')
            time.sleep(1)

    def sendgcode(self):
        print('sending gcode')
        self.cmd("G0 Z-5 F300")
        self.cmd("M114")
        self.wait_for_m114()
        self.check_cond()

    def check_cond(self):
        print('Checking conductive touch...')
        if self.cond is not None and self.cond < self.con_threshold:
            print(f"Conductive touch detected! Conductance: {self.cond}")
        else:
            print(f"No conductive touch detected. Conductance: {self.cond}")

    def wait_for_m114(self):
        position_pattern = re.compile(r"X:(-?\d*\.?\d*) Y:(-?\d*\.?\d*) Z:(-?\d*\.?\d*)")
        while True:
            response = self.get_response(position_pattern)
            if response:
                break
            time.sleep(0.1)

    def get_response(self, pattern, timeout=3):
        start_time = time.time()
        while True:
            rlist, _, _ = select.select([self.console.stdout], [], [], 0.01)
            if rlist:
                output = self.console.stdout.readline().strip()
                print(f"Output: {output}")
                if re.match(pattern, output):
                    return output
            if time.time() - start_time > timeout:
                print("Timeout waiting for response")
                return None
            time.sleep(0.002)

    def cmd(self, cmd_string):
        print(f"Sending command to printer: {cmd_string}")
        if isinstance(cmd_string, str):
            self.console.stdin.write(cmd_string + '\n')
        elif isinstance(cmd_string, list):
            for cmd in cmd_string:
                self.console.stdin.write(cmd + '\n')
                time.sleep(0.01)
        else:
            print('cmd_string is not a string or list')
        self.console.stdin.flush()

    def stop(self):
        self.prtconnect = False
        self.homed = False
        self.console.kill()
        self.console.terminate()
        self.terminate()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    control = console_control()
    control.start()

    # Give time for the console to initialize
    time.sleep(2)

    # Test the conductive touch
    control.sendgcode()

    # Stop the console thread after testing
    control.stop()
    app.exec_()
