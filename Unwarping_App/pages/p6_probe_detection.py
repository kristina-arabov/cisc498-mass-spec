from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt

from Unwarping_App.components.common import CamFeed, LightingDropdown, ProbeDropdown, PortControl, TagOverlay
from Unwarping_App.components.utils import addAllWidgets, updateFrame, unwarpPhoto, getPrinterPosition, setBrightness, updateDropdownIndex

class ProbeDetection(QWidget):
    def __init__(self, camera, light_connection, printer, vars):
        super().__init__()
        self.camera = camera
        self.camera.enable_buttons.connect(self.camConnection)
        
        self.light_connection = light_connection
        self.light_connection.enable_buttons.connect(self.lightConnection)
        
        self.printer = printer
        self.vars = vars

        self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        widgets = []
        layout = QGridLayout()

        control_col = QWidget()
        control_col_layout = QVBoxLayout()

        # Image feed
        self.feed = CamFeed("")
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.feed, frame))

        # corner buttons
        self.next_point = QPushButton("Next corner", objectName="blue")
        self.next_point.clicked.connect(lambda: self.handleCorners("next"))

        self.previous_point = QPushButton("Previous corner", objectName="blue")
        self.previous_point.clicked.connect(lambda: self.handleCorners("previous"))
        self.previous_point.setEnabled(False)

        # april tag overlay
        self.tag_overlay = TagOverlay()
        self.idx = 0
        self.corners_imaged = [False, False, False, False]
        self.tag_overlay.corner_colours[self.idx] = QColor("#212D99")

        # instructions text
        self.instructions = QLabel("Please move the probe to the highlighted blue corner.", objectName="larger")

        # Ports
        self.camera_connection = PortControl("Camera: ")
        self.camera_connection.connect_btn.clicked.connect(lambda: self.camConnection(True))
        self.camera_connection.disconnect_btn.clicked.connect(lambda: self.camConnection(False))
        self.camera_connection.update_btn.clicked.connect(lambda: self.camera_connection.updatePorts(self.camera))
        self.camera_connection.dropdown.currentIndexChanged.connect(lambda: updateDropdownIndex(self.camera, self.camera_connection.dropdown.currentData()))

        self.lighting_control = PortControl("Lighting: ")
        self.lighting_control.connect_btn.clicked.connect(lambda: self.lightConnection(True))
        self.lighting_control.disconnect_btn.clicked.connect(lambda: self.lightConnection(False))
        self.lighting_control.update_btn.clicked.connect(lambda: self.lighting_control.updatePorts(self.light_connection))
        self.lighting_control.dropdown.currentIndexChanged.connect(lambda: updateDropdownIndex(self.light_connection, self.lighting_control.dropdown.currentData()))

        # lighting adjustment
        lighting = LightingDropdown()
        lighting.slider.valueChanged.connect(lambda: setBrightness(lighting, self.light_connection))

        # corner stuff + tag
        self.probe_dropdown = ProbeDropdown()
        self.probe_dropdown.tag_size_input.textChanged.connect(lambda: self.saveTagSize(self.vars, self.probe_dropdown.tag_size_input.text()))

        self.probe_dropdown.bottom_left_X.textChanged.connect(lambda: self.cornerOnChange("bottom_left"))
        self.probe_dropdown.bottom_left_Y.textChanged.connect(lambda: self.cornerOnChange("bottom_left"))

        self.probe_dropdown.top_right_X.textChanged.connect(lambda: self.cornerOnChange("top_right"))
        self.probe_dropdown.top_right_Y.textChanged.connect(lambda: self.cornerOnChange("top_right"))

        # done + capture buttons
        self.done_button = QPushButton("Probe at location", objectName="dark_blue")
        self.done_button.clicked.connect(lambda: self.handleCornerConfirm())

        self.capture_button = QPushButton("Capture photo", objectName="dark_blue")
        self.capture_button.clicked.connect(lambda: self.saveTagPhoto())
        self.capture_button.hide() # hide for now

        widgets.append(self.camera_connection)
        widgets.append(self.lighting_control)
        widgets.append(lighting)
        widgets.append(self.probe_dropdown)
        widgets.append(self.done_button)
        widgets.append(self.capture_button)

        control_col_layout = addAllWidgets(control_col_layout, widgets)
        control_col_layout.setAlignment(self.done_button, Qt.Alignment(0))
        control_col_layout.setAlignment(self.capture_button, Qt.Alignment(0))
        control_col.setLayout(control_col_layout)

        layout.addWidget(self.feed, 0, 0, 1, 4, alignment=Qt.AlignLeft)
        layout.addWidget(self.next_point, 1, 0)
        layout.addWidget(self.tag_overlay, 1, 1, 2, 1)
        layout.addWidget(self.instructions, 1, 2, 2, 1)
        layout.addWidget(self.previous_point, 2, 0)
        layout.addWidget(control_col, 0, 3, 3, 1)


        self.setLayout(layout)


    def handleCorners(self, type):
        if type == "next":
            # Disable the button if the next increment will be the last corner
            if (self.idx + 1) >= 3:
                self.next_point.setEnabled(False)
            
            self.idx += 1
            if self.idx >= 1:
                self.previous_point.setEnabled(True)
            
        elif type == "previous":
            # Disable the button if the next increment will be the first corner
            if (self.idx - 1) == 0:
                self.previous_point.setEnabled(False)

            self.idx -= 1
            
            if self.idx < 3:
                self.next_point.setEnabled(True)
        
        self.setOriginalColors()
        self.tag_overlay.corner_colours[self.idx] = QColor("#212D99")
        self.update()

        self.done_button.show()
        self.capture_button.hide()
        self.instructions.setText("Please move the probe to the highlighted blue corner.")
    
    def setOriginalColors(self):
        for i in range(4):
            self.tag_overlay.corner_colours[i] = QColor("#4FC46E") if self.corners_imaged[i] else QColor("#C5C5C5")
    
    def handleCornerConfirm(self):
        self.done_button.hide()
        self.capture_button.show()
        self.capture_button.setEnabled(True)

        location = getPrinterPosition(self.printer) # TODO change to calibration

        self.instructions.setText("Please move the probe to Z={0}.".format(location[2]))
    
    def saveTagPhoto(self):
        img = self.camera.frame.copy()
        img = unwarpPhoto(img, self.vars["checkerboard"])

        position = getPrinterPosition(self.printer)

        self.vars["tags"]["loc" + str(self.idx)] = position
        self.vars["tags"]["img" + str(self.idx)] = img

        self.instructions.setText("Photo captured successfully!")
        self.corners_imaged[self.idx] = True

        if self.idx == 1:
            self.probe_dropdown.bottom_left_X.setText(str(position[0]))
            self.probe_dropdown.bottom_left_Y.setText(str(position[1]))
        elif self.idx == 3:
            self.probe_dropdown.top_right_X.setText(str(position[0]))
            self.probe_dropdown.top_right_Y.setText(str(position[1]))
    
    def saveTagSize(self, vars, value):
        # Save as float, in case the tag has some mm measurement
        vars["tags"]["size"] = float(value)
    
    def cornerOnChange(self, type):
        if type == "bottom_left":
            x = float(self.probe_dropdown.bottom_left_X.text())
            y = float(self.probe_dropdown.bottom_left_Y.text())
            self.vars["tags"]["bottom_left"] = (x, y)
        
        elif type == "top_right":
            x = float(self.probe_dropdown.top_right_X.text())
            y = float(self.probe_dropdown.top_right_Y.text())
            self.vars["tags"]["top_right"] = (x, y)
    
    def camConnection(self, connected):
        if connected:
            if not self.camera.running:
                try:
                    self.camera.start()
                except:
                    pass
            
            if self.camera.running and self.camera.capture.isOpened():
                self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
        
        elif not connected:
            if self.camera.running:
                self.camera.stop()
        
            self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))
    
    def lightConnection(self, connected):
        if connected:
            if not self.light_connection.running:
                try:
                    self.light_connection.start()
                except:
                    pass
        
            if self.light_connection.running:
                self.lighting_control.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
    
        elif not connected:
            if self.light_connection.running:
                self.light_connection.stop()
            
            self.lighting_control.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))