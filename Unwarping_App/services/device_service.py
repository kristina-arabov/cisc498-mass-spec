
# Toggle handling for devices
def toggle(row, device):
    match row.kind:
        # Camera
        case "camera":
            connect_camera(row, device) if row.toggle.isChecked() else disconnect_camera(row, device)
        # Printer
        case "printer":
            pass
        # Conductance
        case "conductance":
            pass
        # Lights
        case "lights":
            connect_lights(row, device) if row.toggle.isChecked() else disconnect_lights(row, device)


''' CAMERA '''
# Connect camera
def connect_camera(row, camera, deviceIndex=0, resolution=(1280, 720), fps=None, name=None):
    camera.idx = deviceIndex
    camera.resolution = resolution
    
    if not camera.running:
        try:
            camera.start()
            row.set_connected(True)
        except:
            pass
    
    if camera.running and camera.capture.isOpened():
        row.set_connected(True)


# Disconnect camera
def disconnect_camera(row, camera):
    if camera.running:
        camera.stop()

    row.set_connected(False)

    success = True if not camera.capture.isOpened() else False


''' LIGHTS '''
# Connect lights
def connect_lights(row, lights):
    lights.idx = row.port_combo.currentData()


    if not lights.running:
        try:
            lights.start()
            row.set_connected(True)
        except:
            pass

    if lights.running:
        row.set_connected(True)

# Disconnect lights
def disconnect_lights(row, lights):
    if lights.running:
        lights.stop()

    row.set_connected(False)

# Adjust brightness intensity
def set_brightness(value, lights):
    percent = value / 100
    brightness = int(percent * 255)
    try:
        print(brightness)
        if 0 <= brightness <= 255:
            lights.serial_conn.write(str(brightness).encode())
            lights.serial_conn.write(b'\n')
    except:
        pass

def getPrinterPosition(printer):
    while True:
        if printer.line.find('Count') != -1:
            line = printer.line.split()
            pos = [float(line[0][2:]), float(line[1][2:]), float(line[2][2:])]
            break
    
    return pos