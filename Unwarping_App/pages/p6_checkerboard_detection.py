from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from Unwarping_App.components.utils import addAllWidgets, updateFrame, getCheckerboardUnwarp, saveUnwarping, setBrightness, updateDropdownIndex
from Unwarping_App.components.common import CamFeed, LightingDropdown, CheckerboardDropdown, PortControl

class CheckerboardDetection(QWidget):
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