import time


# ── Printer polling constants ──────────────────────────────────────────────────

# Maximum seconds to wait for a position report before giving up.
POSITION_POLL_TIMEOUT_S: float = 15.0

# Interval between polling attempts (seconds).
POSITION_POLL_INTERVAL_S: float = 0.05

# ──────────────────────────────────────────────────────────────────────────────


# Toggle handling for devices
def toggle(row, device):

    # Camera
    if row.kind == "camera":
        connect_camera(row, device) if row.toggle.isChecked() else disconnect_camera(row, device)

    # Printer
    elif row.kind == "printer":
        pass # TODO signal?

    # Conductance
    elif row.kind == "conductance":
        pass # TODO signal?

    # Lights
    elif row.kind == "lights":
        connect_lights(row, device) if row.toggle.isChecked() else disconnect_lights(row, device)

    else:
        pass


# CAMERA FUNCTIONS ---------------------------------------
# Connect camera
def connect_camera(row, camera, resolution=(1280, 720), fps=None, name=None):
    idx = row.port_combo.currentIndex() - 1
    camera.idx = idx if idx >= 0 else None
    camera.resolution = resolution

    if not camera.running and idx >= 0:
        try:
            camera.start()
            row.set_connected(True)
            row.port_combo.setEnabled(False)
        except:
            pass
    
    if camera.running and camera.capture.isOpened():
        row.set_connected(True)



# Disconnect camera
def disconnect_camera(row, camera):
    if camera.running:
        camera.stop()

    row.set_connected(False)
    row.port_combo.setEnabled(True)


# LIGHTS CONTROL FUNCTIONS -------------------------
# Connect lights
def connect_lights(row, lights):
    lights.idx = row.port_combo.currentData()

    if not lights.running:
        try:
            lights.start()
            row.set_connected(True)
            row.port_combo.setEnabled(False)
        except:
            pass

    if lights.running:
        row.set_connected(True)

# Disconnect lights
def disconnect_lights(row, lights):
    if lights.running:
        lights.stop()

    row.set_connected(False)
    row.port_combo.setEnabled(False)


# Adjust brightness intensity
def set_brightness(value, lights):
    percent = value / 100
    brightness = int(percent * 255)
    try:
        if 0 <= brightness <= 255:
            lights.serial_conn.write(str(brightness).encode())
            lights.serial_conn.write(b'\n')
    except:
        pass


# PRINTER FUNCTIONS ----------------------------------------

def getPrinterPosition(printer):
    """Block indefinitely until a position report is received from the printer."""
    while printer.prtconnect:
        if printer.line.find('Count') != -1:
            line = printer.line.split()
            return [float(line[0][2:]), float(line[1][2:]), float(line[2][2:])]


def get_printer_position_timeout(printer, timeout_s=POSITION_POLL_TIMEOUT_S):
    """Poll for a position report, returning [x, y, z] or None on timeout.
    Use this instead of getPrinterPosition() in worker threads.
    """
    time.sleep(POSITION_POLL_INTERVAL_S * 2)
    printer.line = ""
    printer.cmd("M114")

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        line = printer.line
        if line and line.find('Count') != -1:
            try:
                parts = line.split()
                return [float(parts[0][2:]), float(parts[1][2:]), float(parts[2][2:])]
            except (IndexError, ValueError):
                pass
        time.sleep(POSITION_POLL_INTERVAL_S)
    return None


def move_printer_absolute(printer, x, y, z, feed_rate):
    """
    Command the printer to move to an absolute XYZ position.

    Switches to absolute mode (G90), issues the G0 move at feed_rate (mm/min),
    then sends M400 (wait for moves) and M114 (position report request).
    Call get_printer_position_timeout() afterwards to confirm arrival.
    """
    printer.cmd("G90")
    printer.cmd(f"G0 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed_rate}")
    printer.cmd("M400")
    printer.cmd("M114")


def emergency_stop_printer(printer, force_firmware_estop=False):
    """
    Halt motion at the firmware level.

    M410 is Marlin's quick-stop command: it aborts the current move and clears
    queued motion in the planner without waiting for completion. If the target
    firmware does not support M410, set force_firmware_estop=True to also send
    M112, which is a full emergency stop and usually requires a reset before
    further motion.
    """
    if printer is None:
        return

    try:
        printer.cmd("M410")
        if force_firmware_estop:
            printer.cmd("M112")
    except Exception:
        pass


def getConductance(conductance):
    try:
        conductance.sync()
        cap=conductance.read()#reads the conductance value
        capDecode= int(cap.decode("utf-8")) #to decode the value

        conductance.flush()

        return capDecode

    except:
        return 0
