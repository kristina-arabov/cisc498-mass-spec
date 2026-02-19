
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
            pass


# Connect camera
def connect_camera(row, camera, deviceIndex=0, resolution=(1280, 720), fps=None, name=None):
    camera.idx = deviceIndex
    camera.resolution = resolution
    
    if not camera.running:
        try:
            camera.start()
            row.set_connected(True)

            # TODO return values?
            deviceType = row.kind
            connectionId = str(camera.idx)
            status = camera.capture.isOpened()
            lastError = None
            connectedAt = None

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

