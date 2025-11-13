import re
import threading
import queue
import time

class Temperature(QtCore.QThread):
    """
    Class for controlling and monitoring the temperature of the 3D printer.
    Inherits from QThread for separate thread execution.
    """
    def __init__(self, console_control_instance):
        super(Temperature, self).__init__()
        self.printer = console_control_instance
        self.temp_queue = queue.Queue()  # Use the shared queue from the console_control instance
        self.bed_temp = 0
        self.nozzle_temp = 0
        self.flag = True

    def run(self):
        """
        Run the temperature monitoring thread.
        """
        pattern = r"T:(\d*\.?\d*) B:(\d*\.?\d*)"
        print('Monitoring temperature')
        while self.flag:
            if not self.temp_queue.empty():
                output = self.temp_queue.get()
                print('temp', output)
                match = re.match(pattern, output)
                if match:
                    self.nozzle_temp = float(match.group(1))
                    self.bed_temp = float(match.group(2))
                
            self.printer.cmd("M105")  # Get the current temperature
            time.sleep(1)  # Add a delay to avoid spamming the command

    def set_temp(self, temp):
        """
        Set the temperature of the printer.

        Args:
            temp (int): The temperature to set.
        """
        self.printer.cmd(f"M104 S{temp}")  # Set nozzle temperature
        self.printer.cmd(f"M140 S{temp}")  # Set bed temperature

    def stop(self):
        """
        Stop the temperature monitoring thread.
        """
        self.flag = False
        self.terminate()