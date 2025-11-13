from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

import cv2

from Unwarping_App.components.common import CamFeed, ClickableImage,InputField
from Unwarping_App.components.utils import generateProbeAcquisition, updatePixelOverlay, sendLocations

class Location(QWidget):
    def __init__(self, printer, json_path):
        super().__init__()
        self.printer = printer
        self.json_path = json_path
        self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        widgets = []
        layout = QGridLayout()

        self.result = ClickableImage()

        control_col = QWidget()
        layout_col = QVBoxLayout()

        # Inputs for printer movement
        transfer_height = InputField("Transfer height (mm): ")
        spatial_resolution = InputField("Spatial resolution:  ")
        spatial_resolution.input.textChanged.connect(lambda: updatePixelOverlay(self.result, spatial_resolution.input.text(), self.json_path["json"]))

        dwell_time = InputField("Dwell time (s):   ")

        tag_corner = InputField("Tag bottom-left corner: ")

        # Selection buttons for sharpie and ROI
        selection_box = QWidget(objectName="light_blue_box")
        selection_box.setStyleSheet("QWidget { background-color: #C8D3F1; }")
        selection_box_layout = QHBoxLayout()

        selection_label = QLabel("Selection type: ", objectName="larger")

        dot_select = QRadioButton("Dot")
        dot_select.clicked.connect(lambda: self.handle_selection(dot_select))
        dot_select.setChecked(True) # selected on default

        rectangle_select = QRadioButton("Rectangle")
        rectangle_select.clicked.connect(lambda: self.handle_selection(rectangle_select))

        button_group = QButtonGroup()
        button_group.addButton(dot_select)
        button_group.addButton(rectangle_select)

        selection_box_layout.addWidget(selection_label)
        selection_box_layout.addWidget(dot_select)
        selection_box_layout.addWidget(rectangle_select)

        selection_box.setLayout(selection_box_layout)

        # Errors in unwarping (TODO)
        error_box = QWidget(objectName="light_blue_box")
        error_box.setStyleSheet("QWidget { background-color: #C8D3F1; }")
        error_box_layout = QVBoxLayout()

        reprojection_error = QLabel("Reprojection error: ", objectName="larger")
        rms_error = QLabel("RMS error: ", objectName="larger")

        error_box_layout.addWidget(reprojection_error)
        error_box_layout.addWidget(rms_error)

        error_box.setLayout(error_box_layout)

        generate_button = QPushButton("Generate location for regions", objectName="clear")
        generate_button.clicked.connect(lambda: generateProbeAcquisition(self.result.dot, self.result.rectangle, self.json_path["json"], self.printer, self.result, tag_corner))

        send_button = QPushButton("Send to printer", objectName="dark_blue")
        send_button.clicked.connect(lambda: sendLocations(self.result.real_points, dwell_time.input.text(), transfer_height.input.text()))

        # Set layout
        layout.addWidget(self.result, 0, 0, 12, 3, alignment=Qt.AlignLeft)
        layout.addWidget(dwell_time, 2, 4)
        layout.addWidget(transfer_height, 3, 4)
        layout.addWidget(spatial_resolution, 4, 4)
        layout.addWidget(tag_corner, 5, 4)
        layout.addWidget(selection_box, 6, 4, 1, 2)
        layout.addWidget(error_box, 7, 4, 1, 2)
        layout.addWidget(generate_button, 8, 4, 1, 2)
        layout.addWidget(send_button, 9 , 4, 1, 2)

        self.setLayout(layout)

    def handle_selection(self, button):
        self.result.type = button.text()

    def receiveResult(self, img):
        self.result.setNewPixmap(img)
