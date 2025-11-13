# Object to store G-code commands and timestamps
class GCodeItem():
    def __init__(self):
        self.gcode_list = []
        self.completed_gcodes = []

        # Time stamps are stored as seconds since epoch and local time elapsed
        self.time_stamps = []
        self.readable_time_stamps = []


gcodes = GCodeItem()