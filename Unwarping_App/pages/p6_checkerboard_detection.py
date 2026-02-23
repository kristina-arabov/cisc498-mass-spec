from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

from Unwarping_App.components.utils import addAllWidgets, updateFrame, saveUnwarping, setBrightness, updateDropdownIndex
from Unwarping_App.components.common import CamFeed, LightingDropdown, CheckerboardDropdown, PortControl, UnwarpComparison

from Unwarping_App.services import calibration_service, device_service

class CheckerboardDetection(QWidget):
    next = pyqtSignal()

    def __init__(self, camera, lights, printer, transformation):
        super().__init__()
        self.camera = camera
        self.lights = lights
        self.printer = printer

        self.transformation = transformation

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
        component_unwarpComparison = UnwarpComparison()

        ''' RIGHT COLUMN '''
        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_checkerboard = QLabel("Checkerboard Detection", objectName="page_title")

        component_lightControl = LightingDropdown()
        component_checkerboardParams = CheckerboardParamsSection()

        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)

        # Add components
        layout_right.addStretch()
        layout_right.addWidget(label_checkerboard, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(component_lightControl, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(component_checkerboardParams, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(button_next, alignment=Qt.AlignRight)
        layout_right.addStretch()

        # # Allow for scrolling if needed on the user's monitor size
        # scroll_area = QScrollArea()
        # scroll_area.setWidget(right)
        # scroll_area.setWidgetResizable(True) 
        # scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling
        # scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)    # Hide vertical scrollbar 
        # scroll_area.setFrameShape(QFrame.NoFrame) 
        # # scroll_area.setFixedWidth(right_col_width)


        ''' COMPOSE '''
        layout.addWidget(component_unwarpComparison, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(right, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        ''' FUNCTIONS '''
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(component_unwarpComparison.feed, frame))
        component_lightControl.slider.valueChanged.connect(lambda: device_service.set_brightness(component_lightControl.slider.value(), self.lights))
        
        component_unwarpComparison.arrow.button.clicked.connect(lambda: calibration_service.getCheckerboardUnwarp(
                                                                            self.camera, 
                                                                            component_checkerboardParams.input_columns.text(), 
                                                                            component_checkerboardParams.input_rows.text(), 
                                                                            component_unwarpComparison.result,
                                                                            self.transformation,
                                                                            self.printer
                                                                        ))
        

class CheckerboardParamsSection(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)

        label_checkerboardSize = QLabel("Checkerboard size", objectName="larger")
        label_checkerboardSize.setStyleSheet("font-weight: bold;")
        
        ''' ROW 1 '''
        row_1 = QWidget()
        layout_row_1 = QHBoxLayout(row_1)

        label_rows = QLabel("Rows: ")
        self.input_rows = QLineEdit()

        layout_row_1.addWidget(label_rows)
        layout_row_1.addWidget(self.input_rows)


        ''' ROW 2 '''
        row_2 = QWidget()
        layout_row_2 = QHBoxLayout(row_2)

        label_columns = QLabel("Columns: ")
        self.input_columns = QLineEdit()

        layout_row_2.addWidget(label_columns)
        layout_row_2.addWidget(self.input_columns)


        ''' COMPOSE ALL '''
        layout_container.addWidget(label_checkerboardSize)
        layout_container.addWidget(row_1)
        layout_container.addWidget(row_2)

        layout.addWidget(container)

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
        """)
        self.setFixedWidth(375)










''' OLD CODE BELOW '''
    #     widgets = []
    #     layout = QGridLayout()

    #     # Image feed
    #     self.feed = CamFeed("No camera connected.")
    #     self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.feed, frame))
        
    #     self.result = CamFeed("Unwarping results will appear here.")
    #     self.result.hide() # Hide on default

    #     # Camera, result views
    #     show_cam = QPushButton("Camera view", objectName="blue")
    #     show_cam.clicked.connect(lambda: self.handleCam("cam"))

    #     show_result=QPushButton("Result", objectName="blue")
    #     show_result.clicked.connect(lambda: self.handleCam("result"))

    #     control_col = QWidget()
    #     layout_col = QVBoxLayout()

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

    #     # Lighting dropdown + control 
    #     lighting = LightingDropdown()
    #     lighting.slider.valueChanged.connect(lambda: setBrightness(lighting, self.light_connection))

    #     # Checkerboard dropdown
    #     checkerboard = CheckerboardDropdown()

    #     # Save photo
    #     test_photo = QPushButton("Test unwarping", objectName="clear")
    #     test_photo.clicked.connect(lambda: getCheckerboardUnwarp(self.camera.frame.copy(), checkerboard.cols.text(), checkerboard.rows.text(), self.result, self.printer))

    #     save_photo = QPushButton("Use this unwarping", objectName="dark_blue")
    #     save_photo.clicked.connect(lambda: saveUnwarping(self.vars["checkerboard"]))

    #     widgets.append(self.camera_connection)
    #     widgets.append(self.lighting_control)
    #     widgets.append(lighting)
    #     widgets.append(checkerboard)
    #     # widgets.append(save_photo)

    #     layout_col = addAllWidgets(layout_col, widgets)
    #     control_col.setLayout(layout_col)

    #     layout.addWidget(self.feed, 0, 0, 1, 3, alignment=Qt.AlignLeft)
    #     layout.addWidget(self.result, 0, 0, 1, 3, alignment=Qt.AlignLeft)
    #     layout.addWidget(control_col, 0, 2)
    #     layout.addWidget(show_cam, 1, 0)
    #     layout.addWidget(show_result, 1, 1)
    #     layout.addWidget(test_photo, 1, 2)
    #     layout.addWidget(save_photo, 2, 2)

    #     self.setLayout(layout)

    # def handleCam(self, type):
    #     if type == "cam":
    #         self.feed.show()
    #         self.result.hide()
    #     elif type == "result":
    #         self.feed.hide()
    #         self.result.show()
    
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