from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QToolButton, QSlider, QComboBox
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

from Unwarping_App.components.common import CamFeed, LightingDropdown, TagOverlay, TagInformationSection
from Unwarping_App.components.utils import addAllWidgets, updateFrame, unwarpPhoto, getPrinterPosition, setBrightness, updateDropdownIndex

class ProbeDetection(QWidget):
    next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
    # def __init__(self, camera, light_connection, printer, vars):
    #     super().__init__()
    #     self.camera = camera
    #     self.camera.enable_buttons.connect(self.camConnection)
        
    #     self.light_connection = light_connection
    #     self.light_connection.enable_buttons.connect(self.lightConnection)
        
    #     self.printer = printer
    #     self.vars = vars

    #     self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)

        ''' LEFT COLUMN '''
        left = QWidget()
        layout_left = QVBoxLayout(left)

        component_cameraFeed = CamFeed()
        component_tagDiagram = TagInstructions()

        layout_left.addWidget(component_cameraFeed)
        layout_left.addWidget(component_tagDiagram)


        ''' RIGHT COLUMN '''
        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_probeDetection = QLabel("Probe Detection", objectName="page_title")
        # TODO symbol?

        # Lighting control
        component_lightControl = LightingDropdown()

        # Tag information
        component_tagInformation = TagInformationSection()

        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)

        layout_right.addStretch()
        layout_right.addWidget(label_probeDetection, alignment=Qt.AlignLeft)
        layout_right.addWidget(component_lightControl, alignment=Qt.AlignLeft)
        layout_right.addWidget(component_tagInformation, alignment=Qt.AlignLeft)
        layout_right.addWidget(button_next, alignment=Qt.AlignRight)
        layout_right.addStretch()

        layout.addWidget(left)
        layout.addWidget(right)


class TagInstructions(QWidget):
    def __init__(self):
        super().__init__()

        self.idx = 0
        self.corners_imaged = [False, False, False, False]

        layout = QHBoxLayout(self)

        self.component_tagOverlay = TagOverlay()
        self.component_tagOverlay.corner_colours[self.idx] = QColor("#212D99")

        ''' COLUMN 1 '''
        column_1 = QWidget()
        layout_column_1 = QVBoxLayout(column_1)

        self.label_instructions = QLabel("Please manually align the highlighted blue corner with the crosshair.")
        self.label_instructions.adjustSize()
        self.label_instructions.setFixedSize(self.label_instructions.size())

        self.line_progressBar = QProgressBar()
        self.line_progressBar.setRange(0, 100)
        self.line_progressBar.setFormat("%p %") 
        self.line_progressBar.setTextVisible(True)
        self.line_progressBar.setFixedWidth(self.label_instructions.width())

        layout_column_1.addWidget(self.label_instructions, alignment=Qt.AlignLeft)
        layout_column_1.addWidget(self.line_progressBar, alignment=Qt.AlignLeft)


        ''' COLUMN 2 '''
        column_2 = QWidget()
        layout_column_2 = QVBoxLayout(column_2)

        self.button_nextCorner = QPushButton("Next corner", objectName="headerBlue")
        self.button_previousCorner = QPushButton("Previous corner", objectName="clear")
        self.button_previousCorner.setEnabled(False)

        self.button_probeLocation = QPushButton("Probe at location", objectName="blue")

        layout_column_2.addWidget(self.button_nextCorner)
        layout_column_2.addWidget(self.button_previousCorner)
        layout_column_2.addWidget(self.button_probeLocation)


        ''' COMPOSE '''
        layout.addWidget(self.component_tagOverlay)
        layout.addWidget(column_1)
        layout.addWidget(column_2)


        ''' FUNCTIONS '''
        self.button_nextCorner.clicked.connect(lambda: self.handleCorners("next"))
        self.button_previousCorner.clicked.connect(lambda: self.handleCorners("back"))
        self.button_probeLocation.clicked.connect(lambda: self.handleCornerConfirm())


    # Function to properly colour the corners of the tag diagram
    def handleCorners(self, type):
        # Move to next corner
        if type == "next":
            if (self.idx + 1) >= 3:
                self.button_nextCorner.setEnabled(False)    # Disable the button if the next increment will be the last corner
            
            self.idx += 1
            if self.idx >= 1:
                self.button_previousCorner.setEnabled(True)
        
        # Move to previous corner
        elif type == "back":
            if (self.idx - 1) == 0:
                self.button_previousCorner.setEnabled(False) # Disable the button if the next increment will be the first corner

            self.idx -= 1
            
            if self.idx < 3:
                self.button_nextCorner.setEnabled(True)
        
        self.setProbedColors()
        self.component_tagOverlay.corner_colours[self.idx] = QColor("#212D99")

        if self.corners_imaged[self.idx]:
            self.label_instructions.setText("Corner aligned!")
        else:
            self.label_instructions.setText("Please manually align the highlighted blue corner with the crosshair.")

        self.update()


    # Function to acquire the probe's position in alignment with a specific tag corner
    def handleCornerConfirm(self):
        # img = self.camera.frame.copy()
        # img = unwarpPhoto(img, self.vars["checkerboard"])

        # position = getPrinterPosition(self.printer)

        # self.vars["tags"]["loc" + str(self.idx)] = position
        # self.vars["tags"]["img" + str(self.idx)] = img

        self.label_instructions.setText("Corner aligned!")
        self.corners_imaged[self.idx] = True

        # Update progress bar status
        corners_probed = int(((self.corners_imaged.count(True))/ len(self.corners_imaged)) * 100)

        self.line_progressBar.setValue(corners_probed)

        # TODO set input of bottom/top-left rows
        # if self.idx == 1:
        #     self.probe_dropdown.bottom_left_X.setText(str(position[0]))
        #     self.probe_dropdown.bottom_left_Y.setText(str(position[1]))
        # elif self.idx == 3:
        #     self.probe_dropdown.top_right_X.setText(str(position[0]))
        #     self.probe_dropdown.top_right_Y.setText(str(position[1]))


    # Function to set colours to probed or not probed corners
    def setProbedColors(self):
        for i in range(4):
            self.component_tagOverlay.corner_colours[i] = QColor("#4FC46E") if self.corners_imaged[i] else QColor("#C5C5C5")
    


''' OLD CODE BELOW '''
    #     widgets = []
    #     layout = QGridLayout()

    #     control_col = QWidget()
    #     control_col_layout = QVBoxLayout()

    #     # Image feed
    #     self.feed = CamFeed("")
    #     self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.feed, frame))

    #     # corner buttons
    #     self.button_nextCorner = QPushButton("Next corner", objectName="blue")
    #     self.button_nextCorner.clicked.connect(lambda: self.handleCorners("next"))

    #     self.button_previousCorner = QPushButton("Previous corner", objectName="blue")
    #     self.button_previousCorner.clicked.connect(lambda: self.handleCorners("previous"))
    #     self.button_previousCorner.setEnabled(False)

    #     # april tag overlay
    #     self.tag_overlay = TagOverlay()
    #     self.idx = 0
    #     self.corners_imaged = [False, False, False, False]
    #     self.tag_overlay.corner_colours[self.idx] = QColor("#212D99")

    #     # instructions text
    #     self.instructions = QLabel("Please move the probe to the highlighted blue corner.", objectName="larger")

    #     # Ports
    #     self.camera_connection = PortControl("Camera: ")
    #     self.camera_connection.connect_btn.clicked.connect(lambda: self.camConnection(True))
    #     self.camera_connection.disconnect_btn.clicked.connect(lambda: self.camConnection(False))
    #     self.camera_connection.update_btn.clicked.connect(lambda: self.camera_connection.updatePorts(self.camera))
    #     self.camera_connection.dropdown.currentIndexChanged.connect(lambda: updateDropdownIndex(self.camera, self.camera_connection.dropdown.currentData()))

    #     self.lighting_control = PortControl("Lighting: ")
    #     self.lighting_control.connect_btn.clicked.connect(lambda: self.lightConnection(True))
    #     self.lighting_control.disconnect_btn.clicked.connect(lambda: self.lightConnection(False))
    #     self.lighting_control.update_btn.clicked.connect(lambda: self.lighting_control.updatePorts(self.light_connection))
    #     self.lighting_control.dropdown.currentIndexChanged.connect(lambda: updateDropdownIndex(self.light_connection, self.lighting_control.dropdown.currentData()))

    #     # lighting adjustment
    #     lighting = LightingDropdown()
    #     lighting.slider.valueChanged.connect(lambda: setBrightness(lighting, self.light_connection))

    #     # corner stuff + tag
    #     self.probe_dropdown = ProbeDropdown()
    #     self.probe_dropdown.tag_size_input.textChanged.connect(lambda: self.saveTagSize(self.vars, self.probe_dropdown.tag_size_input.text()))

    #     self.probe_dropdown.bottom_left_X.textChanged.connect(lambda: self.cornerOnChange("bottom_left"))
    #     self.probe_dropdown.bottom_left_Y.textChanged.connect(lambda: self.cornerOnChange("bottom_left"))

    #     self.probe_dropdown.top_right_X.textChanged.connect(lambda: self.cornerOnChange("top_right"))
    #     self.probe_dropdown.top_right_Y.textChanged.connect(lambda: self.cornerOnChange("top_right"))

    #     # done + capture buttons
    #     self.done_button = QPushButton("Probe at location", objectName="dark_blue")
    #     self.done_button.clicked.connect(lambda: self.handleCornerConfirm())

    #     self.capture_button = QPushButton("Capture photo", objectName="dark_blue")
    #     self.capture_button.clicked.connect(lambda: self.saveTagPhoto())
    #     self.capture_button.hide() # hide for now

    #     widgets.append(self.camera_connection)
    #     widgets.append(self.lighting_control)
    #     widgets.append(lighting)
    #     widgets.append(self.probe_dropdown)
    #     widgets.append(self.done_button)
    #     widgets.append(self.capture_button)

    #     control_col_layout = addAllWidgets(control_col_layout, widgets)
    #     control_col_layout.setAlignment(self.done_button, Qt.Alignment(0))
    #     control_col_layout.setAlignment(self.capture_button, Qt.Alignment(0))
    #     control_col.setLayout(control_col_layout)

    #     layout.addWidget(self.feed, 0, 0, 1, 4, alignment=Qt.AlignLeft)
    #     layout.addWidget(self.button_nextCorner, 1, 0)
    #     layout.addWidget(self.tag_overlay, 1, 1, 2, 1)
    #     layout.addWidget(self.instructions, 1, 2, 2, 1)
    #     layout.addWidget(self.button_previousCorner, 2, 0)
    #     layout.addWidget(control_col, 0, 3, 3, 1)


    #     self.setLayout(layout)




    # def saveTagSize(self, vars, value):
    #     # Save as float, in case the tag has some mm measurement
    #     vars["tags"]["size"] = float(value)
    
    # def cornerOnChange(self, type):
    #     if type == "bottom_left":
    #         x = float(self.probe_dropdown.bottom_left_X.text())
    #         y = float(self.probe_dropdown.bottom_left_Y.text())
    #         self.vars["tags"]["bottom_left"] = (x, y)
        
    #     elif type == "top_right":
    #         x = float(self.probe_dropdown.top_right_X.text())
    #         y = float(self.probe_dropdown.top_right_Y.text())
    #         self.vars["tags"]["top_right"] = (x, y)
    
    # def camConnection(self, connected):
    #     if connected:
    #         if not self.camera.running:
    #             try:
    #                 self.camera.start()
    #             except:
    #                 pass
            
    #         if self.camera.running and self.camera.capture.isOpened():
    #             self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
        
    #     elif not connected:
    #         if self.camera.running:
    #             self.camera.stop()
        
    #         self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))
    
    # def lightConnection(self, connected):
    #     if connected:
    #         if not self.light_connection.running:
    #             try:
    #                 self.light_connection.start()
    #             except:
    #                 pass
        
    #         if self.light_connection.running:
    #             self.lighting_control.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
    
    #     elif not connected:
    #         if self.light_connection.running:
    #             self.light_connection.stop()
            
    #         self.lighting_control.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))