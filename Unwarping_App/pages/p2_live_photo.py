from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

import cv2
import json

from Unwarping_App.components.common import LightingDropdown, PortControl, CamFeed
from Unwarping_App.components.utils import addAllWidgets, updateFrame, setBrightness, updateDropdownIndex, unwarpPhoto

class LivePhoto(QWidget):
    resultAvailable = pyqtSignal(object)

    def __init__(self, size, camera, light_connection, json_path):
        super().__init__()
        self.size = size
        self.camera = camera
        self.camera.enable_buttons.connect(self.camConnection)

        self.light_connection = light_connection
        self.light_connection.enable_buttons.connect(self.lightConnection)

        self.json_path = json_path
        self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        widgets = []
        layout = QGridLayout()

        # Image feed
        self.feed = CamFeed("")
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.feed, frame))

        self.result = CamFeed("")
        self.result.hide() # Hide on default

        # Camera, result views
        show_cam = QPushButton("Camera view", objectName="blue")
        show_cam.clicked.connect(lambda: self.handleCam("cam"))

        show_result=QPushButton("Result", objectName="blue")
        show_result.clicked.connect(lambda: self.handleCam("result"))
        show_result.setEnabled(False)
        
        control_col = QWidget()
        layout_col = QVBoxLayout()

        # Port Controls 
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
        
        # Lighting dropdown
        self.lighting = LightingDropdown()
        self.lighting.slider.valueChanged.connect(lambda: setBrightness(self.lighting, self.light_connection))

        # Save photo
        self.save_photo = QPushButton("Take Photo and Unwarp", objectName="dark_blue")
        self.save_photo.clicked.connect(lambda: self.onbtnclicked(self.result, show_result))
        self.save_photo.setEnabled(False)

        widgets.append(self.camera_connection)
        widgets.append(self.lighting_control)
        widgets.append(self.lighting)
        widgets.append(self.save_photo)

        layout_col = addAllWidgets(layout_col, widgets)
        control_col.setLayout(layout_col)

        layout.addWidget(self.feed, 0, 0, 1, 3, alignment=Qt.AlignLeft)
        layout.addWidget(self.result, 0, 0, 1, 3, alignment=Qt.AlignLeft)
        layout.addWidget(control_col, 0, 2)
        layout.addWidget(show_cam, 1, 0)
        layout.addWidget(show_result, 1, 1)

        self.setLayout(layout)

        
    
    def handleCam(self, type):
        if type == "cam":
            self.feed.show()
            self.result.hide()
        elif type == "result":
            self.feed.hide()
            self.result.show()

    def onbtnclicked(self, result, show_result):
        # open json file unless there's an error
        try:
            with open(self.json_path["json"], encoding="utf-8") as fh:
                params = json.load(fh)         # a Python dict
        except FileNotFoundError:
            print(f"Cannot find JSON file: {self.json_path['json']}")
            return
        except json.JSONDecodeError as err:
            print(f"JSON syntax error: {err}")
            
        # Get unwarping variables specifically
        params = params["checkerboard"][0]

        # get image from the camera and unwarp it
        img = self.camera.frame.copy()
        img = unwarpPhoto(img,params)
        self.resultAvailable.emit(img)

        #display image
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled = q_img.scaled(result.feed_width, result.feed_height, Qt.KeepAspectRatio)
        result.image_label.setPixmap(QPixmap.fromImage(scaled))
        show_result.setEnabled(True)

    def camConnection(self, connected):
        if connected:
            if not self.camera.running:
                try:
                    self.camera.start()
                except:
                    pass
            
            if self.camera.running and self.camera.capture.isOpened():
                self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
                self.save_photo.setEnabled(True)
        
        elif not connected:
            if self.camera.running:
                self.camera.stop()
        
            self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))
            self.save_photo.setEnabled(False)

    
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
