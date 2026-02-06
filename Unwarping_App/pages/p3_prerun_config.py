from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

import cv2

from Unwarping_App.components.common import CamFeed, ClickableImage,InputField
from Unwarping_App.components.utils import generateProbeAcquisition, updatePixelOverlay, sendLocations

class ModeSelection(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QHBoxLayout(container)

        label_mode = QLabel("Sampling mode: ", objectName="larger")
        label_mode.setStyleSheet("font-weight: bold;")

        button_constantZ = QRadioButton("Constant-Z")
        button_conductive = QRadioButton("Conductive")

        mode_group = QButtonGroup()
        mode_group.addButton(button_constantZ, 0)
        mode_group.addButton(button_conductive, 1)

        button_constantZ.setChecked(True)

        layout_container.addWidget(label_mode)
        layout_container.addWidget(button_constantZ)
        layout_container.addWidget(button_conductive)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("background-color: #C8D3F1;")

class SamplingParameters(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)


        label_samplingParameters = QLabel("Sampling parameters: ", objectName="larger")
        label_samplingParameters.setStyleSheet("font-weight: bold;")

        ''' ROW 1 '''
        row_1 = QWidget()
        layout_row_1 = QHBoxLayout(row_1)

        label_spatialRes = QLabel("Spatial resolution (mm): ")
        input_spatialRes = QLineEdit()

        layout_row_1.addWidget(label_spatialRes)
        layout_row_1.addWidget(input_spatialRes)   


        ''' ROW 2 '''
        row_2 = QWidget()
        layout_row_2 = QHBoxLayout(row_2)

        label_dwell = QLabel("Dwell time (s): ")
        input_dwell = QLineEdit()

        layout_row_2.addWidget(label_dwell)
        layout_row_2.addWidget(input_dwell)


        ''' ROW 3 '''
        row_3 = QWidget()
        layout_row_3 = QHBoxLayout(row_3)

        label_transfer = QLabel("Transfer height (mm): ")
        input_transfer = QLineEdit()

        layout_row_3.addWidget(label_transfer)
        layout_row_3.addWidget(input_transfer)

        ''' ROW 4 '''
        row_4 = QWidget()
        layout_row_4 = QHBoxLayout(row_4)

        # TODO
        label_drag = QLabel("Drag sampling?")

        layout_row_4.addWidget(label_drag)


        layout_container.addWidget(label_samplingParameters)
        layout_container.addWidget(row_1)
        layout_container.addWidget(row_2)
        layout_container.addWidget(row_3)
        layout_container.addWidget(row_4)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
        """)


class PrerunConfig(QWidget):
    next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        
    # def __init__(self, printer, json_path):
    #     super().__init__()
    #     self.printer = printer
    #     self.json_path = json_path
    #     self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())


        layout = QHBoxLayout(self)
        component_resultImg = CamFeed()

        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_prerun = QLabel("Pre-run Config", objectName="page_title")
        # TODO logo?

        ''' SAMPLING MODE SELECTION '''
        component_samplingMode = ModeSelection()

        ''' PARAMETER INPUTS '''
        component_samplingParams = SamplingParameters()

        button_startRun = QPushButton("Start sampling run", objectName="blue")
        button_startRun.clicked.connect(self.next.emit)

        ''' ASSEMBLE RIGHT COLUMN '''
        layout_right.addStretch()
        layout_right.addWidget(label_prerun)
        layout_right.addWidget(component_samplingMode)
        layout_right.addWidget(component_samplingParams)
        layout_right.addStretch()
        layout_right.addWidget(button_startRun)
        layout_right.addStretch()

        # layout_right.setContentsMargins(0, 0, 0, 0) 
        # layout_right.setSpacing(0)  

        ''' COMPOSE ALL '''
        layout.addWidget(component_resultImg)
        layout.addWidget(right)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  



    #     widgets = []
    #     layout = QGridLayout()

    #     self.result = ClickableImage()

    #     control_col = QWidget()
    #     layout_col = QVBoxLayout()

    #     # Inputs for printer movement
    #     transfer_height = InputField("Transfer height (mm): ")
    #     spatial_resolution = InputField("Spatial resolution:  ")
    #     spatial_resolution.input.textChanged.connect(lambda: updatePixelOverlay(self.result, spatial_resolution.input.text(), self.json_path["json"]))

    #     dwell_time = InputField("Dwell time (s):   ")

    #     tag_corner = InputField("Tag bottom-left corner: ")

    #     # Selection buttons for sharpie and ROI
    #     selection_box = QWidget(objectName="light_blue_box")
    #     selection_box.setStyleSheet("QWidget { background-color: #C8D3F1; }")
    #     selection_box_layout = QHBoxLayout()

    #     selection_label = QLabel("Selection type: ", objectName="larger")

    #     dot_select = QRadioButton("Dot")
    #     dot_select.clicked.connect(lambda: self.handle_selection(dot_select))
    #     dot_select.setChecked(True) # selected on default

    #     rectangle_select = QRadioButton("Rectangle")
    #     rectangle_select.clicked.connect(lambda: self.handle_selection(rectangle_select))

    #     button_group = QButtonGroup()
    #     button_group.addButton(dot_select)
    #     button_group.addButton(rectangle_select)

    #     selection_box_layout.addWidget(selection_label)
    #     selection_box_layout.addWidget(dot_select)
    #     selection_box_layout.addWidget(rectangle_select)

    #     selection_box.setLayout(selection_box_layout)

    #     # Errors in unwarping (TODO)
    #     error_box = QWidget(objectName="light_blue_box")
    #     error_box.setStyleSheet("QWidget { background-color: #C8D3F1; }")
    #     error_box_layout = QVBoxLayout()

    #     reprojection_error = QLabel("Reprojection error: ", objectName="larger")
    #     rms_error = QLabel("RMS error: ", objectName="larger")

    #     error_box_layout.addWidget(reprojection_error)
    #     error_box_layout.addWidget(rms_error)

    #     error_box.setLayout(error_box_layout)

    #     generate_button = QPushButton("Generate location for regions", objectName="clear")
    #     generate_button.clicked.connect(lambda: generateProbeAcquisition(self.result.dot, self.result.rectangle, self.json_path["json"], self.printer, self.result, tag_corner))

    #     send_button = QPushButton("Send to printer", objectName="dark_blue")
    #     send_button.clicked.connect(lambda: sendLocations(self.result.real_points, dwell_time.input.text(), transfer_height.input.text()))

    #     # Set layout
    #     layout.addWidget(self.result, 0, 0, 12, 3, alignment=Qt.AlignLeft)
    #     layout.addWidget(dwell_time, 2, 4)
    #     layout.addWidget(transfer_height, 3, 4)
    #     layout.addWidget(spatial_resolution, 4, 4)
    #     layout.addWidget(tag_corner, 5, 4)
    #     layout.addWidget(selection_box, 6, 4, 1, 2)
    #     layout.addWidget(error_box, 7, 4, 1, 2)
    #     layout.addWidget(generate_button, 8, 4, 1, 2)
    #     layout.addWidget(send_button, 9 , 4, 1, 2)

    #     self.setLayout(layout)

    # def handle_selection(self, button):
    #     self.result.type = button.text()

    # def receiveResult(self, img):
    #     self.result.setNewPixmap(img)
