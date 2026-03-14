
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
    pos = None

    while True:
        if printer.line.find('Count') != -1:
            line = printer.line.split()
            pos = [float(line[0][2:]), float(line[1][2:]), float(line[2][2:])]
            break

    return pos
